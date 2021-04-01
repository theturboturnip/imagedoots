from typing import List, Callable

from PIL import Image

from libimagedoots.common import Signal


def convert_to_signals(im: Image, reset_signals: int=5, hporch_front: int=1, hporch_back: int=1, hsync_len: int=1, vporch_front: int=1, vporch_back: int=1, vsync_len: int=2, border: int = 2) -> List[Signal]:
    """
    Converts im to a list of signals that would get sent to the RBG converter using the VGA protocol.
    """
    signals: List[Signal] = [Signal.reset_signal()] * reset_signals

    xlen, ylen = im.size
    pixel_access = im.load()


    # https://learn.digilentinc.com/Documents/269
    # Number of columns, or "signals within row"
    row_signal_count = hsync_len + hporch_back + border + xlen + border + hporch_front
    row_count = vsync_len + vporch_back + border + ylen + border + vporch_front

    for y in range(row_count):
        valid_y = y - (vsync_len + vporch_back + border)
        vsync: bool = y < vsync_len

        generate_from_image_x: Callable[[int], Signal]
        if 0 <= valid_y and valid_y < ylen:
            generate_from_image_x = lambda valid_x: Signal.pixel_signal(pixel_access[valid_x, valid_y])
        else:
            generate_from_image_x = lambda valid_x: Signal.offscreen_signal(vsync=vsync)

        for x in range(row_signal_count):
            hsync = x < hsync_len

            valid_x = x - (hsync_len + hporch_back + border)
            if 0 <= valid_x and valid_x < xlen:
                signals.append(generate_from_image_x(valid_x))
            else:
                signals.append(Signal.offscreen_signal(hsync=hsync, vsync=vsync))
            pass
        pass

    return signals


def serialize_signals(sigs: List[Signal]) -> str:
    return "\n".join(
        str(s)
        for s in sigs
    )