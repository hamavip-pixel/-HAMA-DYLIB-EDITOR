
# HAMA DYLIB EDITOR

A GitHub Actions project for detecting common embedded image formats in DYLIB files.

## Usage

1. Upload a `.dylib` file into the `input/` folder.
2. Open GitHub Actions.
3. Select HAMA DYLIB EDITOR.
4. Click Run workflow.
5. Download the HAMA-DYLIB-EXTRACTED artifact.

## Supported image signatures

- PNG
- JPEG
- GIF
- BMP

## Important

Image extraction is best-effort. Not every DYLIB stores images as standalone files.

The replacement script currently preserves the original binary and does not modify images. Safe replacement requires verified image offsets, sizes, and binary layout.
