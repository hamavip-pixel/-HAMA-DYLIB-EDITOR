
import os
import sys
import json
import hashlib

MAGIC = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"BM": "bmp",
}

def get_image_end(data, start, extension):
    if extension == "png":
        pos = data.find(b"IEND", start + 8)
        return pos + 8 if pos != -1 and pos + 8 <= len(data) else None

    if extension == "jpg":
        pos = data.find(b"\xff\xd9", start + 3)
        return pos + 2 if pos != -1 else None

    if extension == "gif":
        pos = data.find(b"\x3b", start + 6)
        return pos + 1 if pos != -1 else None

    if extension == "bmp":
        if start + 6 > len(data):
            return None
        size = int.from_bytes(data[start + 2:start + 6], "little")
        return start + size if 14 <= size <= len(data) - start else None

    return None

def extract_images(path):
    os.makedirs("images", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    with open(path, "rb") as f:
        data = f.read()

    manifest = []
    seen = set()

    for magic, extension in MAGIC.items():
        position = 0

        while True:
            position = data.find(magic, position)

            if position == -1:
                break

            end = get_image_end(data, position, extension)

            if end is None:
                position += len(magic)
                continue

            image_data = data[position:end]
            digest = hashlib.sha256(image_data).hexdigest()

            if digest not in seen:
                seen.add(digest)

                filename = f"image_{len(manifest)+1}_{digest[:12]}.{extension}"

                with open(os.path.join("images", filename), "wb") as out:
                    out.write(image_data)

                manifest.append({
                    "filename": filename,
                    "offset": position,
                    "size": len(image_data),
                    "format": extension,
                    "sha256": digest
                })

            position = end

    manifest_path = "output/image_manifest.json"

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Images found: {len(manifest)}")
    print(f"Manifest saved: {manifest_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_images.py file.dylib")
        sys.exit(1)

    extract_images(sys.argv[1])
