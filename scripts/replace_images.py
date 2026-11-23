
import os
import sys
import io
import json
import hashlib
from PIL import Image

MANIFEST = "output/image_manifest.json"
ORIGINAL_IMAGES = "images"

def encode_jpeg(image, max_size):
    width, height = image.size

    while width >= 1 and height >= 1:
        resized = image.resize((width, height), Image.Resampling.LANCZOS)

        for quality in range(95, 0, -2):
            buffer = io.BytesIO()

            resized.save(
                buffer,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=False
            )

            jpeg = buffer.getvalue()

            # Reserve at least 4 bytes for a valid JPEG comment segment.
            if len(jpeg) <= max_size - 4:
                padding = max_size - len(jpeg)

                comment_payload_size = padding - 4
                comment_length = comment_payload_size + 2

                comment = (
                    b"\xff\xfe"
                    + comment_length.to_bytes(2, "big")
                    + (b"\x00" * comment_payload_size)
                )

                final_jpeg = jpeg[:-2] + comment + jpeg[-2:]

                if len(final_jpeg) == max_size:
                    return final_jpeg, width, height, quality

        if width == 1 and height == 1:
            break

        width = max(1, int(width * 0.85))
        height = max(1, int(height * 0.85))

    raise ValueError("Could not fit JPEG into the original image slot.")

def replace_images(original, replacements, output):
    if not os.path.isfile(MANIFEST):
        raise SystemExit("ERROR: image_manifest.json not found")

    with open(MANIFEST, "r") as f:
        manifest = json.load(f)

    with open(original, "rb") as f:
        data = bytearray(f.read())

    changed = 0

    for item in manifest:
        filename = item["filename"]
        offset = item["offset"]
        size = item["size"]
        expected_hash = item["sha256"]

        replacement_path = os.path.join(replacements, filename)
        original_image_path = os.path.join(ORIGINAL_IMAGES, filename)

        if not os.path.isfile(replacement_path):
            print(f"Skipped (missing): {filename}")
            continue

        if offset < 0 or size <= 0 or offset + size > len(data):
            print(f"Skipped (invalid offset): {filename}")
            continue

        current_hash = hashlib.sha256(
            data[offset:offset + size]
        ).hexdigest()

        if current_hash != expected_hash:
            print(f"Skipped (original mismatch): {filename}")
            continue

        try:
            with Image.open(replacement_path) as source:
                image = source.convert("RGB")

            if os.path.isfile(original_image_path):
                with Image.open(original_image_path) as old:
                    image.thumbnail(
                        (max(old.width, image.width), max(old.height, image.height))
                    )

            new_image, width, height, quality = encode_jpeg(image, size)

            data[offset:offset + size] = new_image

            changed += 1

            print(f"Replaced: {filename}")
            print(f"  Final size: {len(new_image)} bytes")
            print(f"  Dimensions: {width}x{height}")
            print(f"  JPEG quality: {quality}")

        except Exception as error:
            print(f"ERROR replacing {filename}: {error}")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    with open(output, "wb") as f:
        f.write(data)

    print(f"Replaced images: {changed}")
    print(f"Output: {output}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: replace_images.py original.dylib replacements output.dylib")
        sys.exit(1)

    replace_images(sys.argv[1], sys.argv[2], sys.argv[3])
