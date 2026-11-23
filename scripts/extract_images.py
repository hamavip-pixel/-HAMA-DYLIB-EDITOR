
import sys
import os
import struct
import hashlib

MAGIC = {
    b"\x89PNG\r\n\x1a\n": ("png", 8),
    b"\xff\xd8\xff": ("jpg", 3),
    b"GIF87a": ("gif", 6),
    b"GIF89a": ("gif", 6),
    b"BM": ("bmp", 2),
}

def extract_images(path):
    os.makedirs("images", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    with open(path, "rb") as f:
        data = f.read()

    found = 0

    for magic, (extension, offset) in MAGIC.items():
        position = 0

        while True:
            position = data.find(magic, position)

            if position == -1:
                break

            end = None

            if extension == "png":
                marker = data.find(b"IEND", position + 8)
                if marker != -1 and marker + 8 <= len(data):
                    end = marker + 8

            elif extension == "jpg":
                marker = data.find(b"\xff\xd9", position + 3)
                if marker != -1:
                    end = marker + 2

            elif extension == "gif":
                marker = data.find(b"\x3b", position + 6)
                if marker != -1:
                    end = marker + 1

            elif extension == "bmp" and position + 6 <= len(data):
                size = struct.unpack_from("<I", data, position + 2)[0]
                if 14 <= size <= len(data) - position:
                    end = position + size

            if end and end > position:
                image_data = data[position:end]

                name = hashlib.sha256(image_data).hexdigest()[:12]
                filename = f"image_{found + 1}_{name}.{extension}"

                with open(os.path.join("images", filename), "wb") as out:
                    out.write(image_data)

                found += 1
                position = end
            else:
                position += len(magic)

    print(f"Extracted {found} possible images.")

    if found == 0:
        print("No supported embedded images were detected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_images.py file.dylib")
        sys.exit(1)

    extract_images(sys.argv[1])
