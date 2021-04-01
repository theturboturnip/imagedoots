import argparse
from pathlib import Path

from PIL import Image

from libimagedoots import exporter, importer

EXT=".imgsigs"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    args = parser.parse_args()

    filepath = Path(args.file)

    if filepath.suffix == ".imgsigs":
        # Deserialize signals and create pixels while the file is open - signals is an iterator, not a list
        with open(filepath, "r") as f:
            f.seek(0)
            pixels = importer.signals_to_pixels(importer.deserialize_signals(f))
        im = importer.pixels_to_image(pixels)
        im.save(str(filepath) + ".png")
    else:
        # Try to encode the image as signals
        im = Image.open(filepath)
        signals = exporter.convert_to_signals(im)
        signals_encoded = exporter.serialize_signals(signals)
        with open(str(filepath) + EXT, "w") as f:
            f.write(signals_encoded)