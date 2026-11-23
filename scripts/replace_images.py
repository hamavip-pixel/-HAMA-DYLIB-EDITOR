
import os
import sys
import hashlib

def replace_images(original, replacements, output):
    with open(original, "rb") as f:
        data = bytearray(f.read())

    changed = 0

    for filename in sorted(os.listdir(replacements)):
        replacement_path = os.path.join(replacements, filename)

        if not os.path.isfile(replacement_path):
            continue

        with open(replacement_path, "rb") as f:
            new_image = f.read()

        print(f"Checking: {filename}")

        # A safe binary replacement needs the exact original
        # byte range, not only the extracted image filename.
        print("Skipped: verified original offset is not available.")

    with open(output, "wb") as f:
        f.write(data)

    print(f"Replacements completed: {changed}")
    print("Output:", output)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: replace_images.py original.dylib replacements output.dylib")
        sys.exit(1)

    replace_images(sys.argv[1], sys.argv[2], sys.argv[3])
