from typing import List, TextIO, Iterator, Generator

from PIL import Image

from libimagedoots.common import Signal, Pixel


def deserialize_signals(f: TextIO) -> Iterator[Signal]:
    for line in f:
        line = line.rstrip()
        yield Signal.from_string(line)


def signals_to_pixels(signals: Iterator[Signal]) -> List[List[Pixel]]:
    pixels: List[List[Pixel]] = []
    current_row: List[Pixel] = []

    current_row_idx = -1
    vsync_rows = 0

    last_vsync = False
    last_hsync = False
    for s in signals:
        if not s.n_rst:
            # Reset
            if pixels or current_row:
                raise ValueError("Got a reset signal while pixels/current_row had data.")
            last_hsync = False
            last_vsync = False
            continue
        else:
            if s.hsync != last_hsync:
                if s.hsync:
                    # We've started a new row!
                    current_row_idx += 1
                    # if the current row has vsync, mark it as a vsync row
                    if s.vsync:
                        vsync_rows += 1

                    # If we have pixels in the current row...
                    if current_row:
                        # Add them to the image, a new row has started
                        pixels.append(current_row)
                        current_row = []
                    # Otherwise just wait for the hsync to stop
                    pass
                pass

            if not s.vsync and not s.hsync and s.vde:
                current_row.append(s.color)

            last_hsync = s.hsync
            last_vsync = s.vsync
            pass
        pass

    # If there are still pixels and we didn't get an hsync at the end, add the data
    if current_row:
        pixels.append(current_row)

    return pixels


def pixels_to_image(pixel_rows: List[List[Pixel]]) -> Image:
    if len(pixel_rows) == 0:
        raise ValueError(f"pixel_rows has no data")
    pixel_row_lengths = set(len(row) for row in pixel_rows)
    if len(pixel_row_lengths) > 1:
        raise ValueError(f"multiple lengths of pixel_row: {pixel_row_lengths}")

    size = (pixel_row_lengths.pop(), len(pixel_rows))
    im = Image.new('RGB', size)
    pixels = im.load()

    for y in range(size[1]):
        for x in range(size[0]):
            pixels[x, y] = pixel_rows[y][x].as_tuple()

    return im
