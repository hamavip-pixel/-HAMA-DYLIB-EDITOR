
import os
import sys
import json
import hashlib

def replace_images(original, replacements, output):
    manifest_path = "output/image_manifest.json"

    if not os.path.isfile(manifest_path):
        raise SystemExit("ERROR: image_manifest.json not found")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    with open(original, "rb") as f:
        data = bytearray(f.read())

    changed = 0

    for item in manifest:
        filename = item["filename"]
        replacement_path = os.path.join(replacements, filename)

        if not os.path.isfile(replacement_path):
            print(f"Skipped (missing): {filename}")
            continue

        with open(replacement_path, "rb") as f:
            new_image = f.read()

        offset = item["offset"]
        size = item["size"]

        if len(new_image) != size:
            print(f"Skipped (size mismatch): {filename}")
            continue

        if hashlib.sha256(data[offset:offset + size]).hexdigest() != item["sha256"]:
            print(f"Skipped (original mismatch): {filename}")
            continue

        data[offset:offset + size] = new_image
        changed += 1
        print(f"Replaced: {filename}")

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
