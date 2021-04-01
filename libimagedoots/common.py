from dataclasses import dataclass
from typing import Tuple, Union

import parse


@dataclass(frozen=True)
class Pixel:
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255

    @staticmethod
    def PURPLE():
        return Pixel(255, 0, 255)

    def as_tuple(self) -> Tuple[int,int,int]:
        return self.r, self.g, self.b


# class SignalType(Enum):
#     RESET       = 0b0001
#     HSYNC       = 0b1010
#     VSYNC       = 0b1100
#     H_AND_VSYNC = 0b1110
#     OFFSCREEN   = 0b1000

@dataclass(frozen=True)
class Signal:
    color: Pixel
    hsync: bool
    vsync: bool
    # VDE =
    vde: bool  # Video Enable?
    n_rst: bool

    # clk not included, set by verilog testbench

    PATTERN=parse.compile("{n_rst:1b} {color_r:02x} {color_b:02x} {color_g:02x} {hsync:1b} {vsync:1b} {vde:1b}")

    @staticmethod
    def from_string(data: str) -> 'Signal':
        vals = Signal.PATTERN.parse(data)
        return Signal(
            color=Pixel(
                r=vals['color_r'],
                g=vals['color_g'],
                b=vals['color_b']
            ),
            hsync=bool(vals['hsync']),
            vsync=bool(vals['vsync']),
            vde=bool(vals['vde']),
            n_rst=bool(vals['n_rst'])
        )

    def __str__(s):
        return f"{int(s.n_rst):1b} {s.color.r:02x} {s.color.b:02x} {s.color.g:02x} {int(s.hsync):1b} {int(s.vsync):1b} {int(s.vde):1b}"

    @staticmethod
    def reset_signal() -> 'Signal':
        return Signal(
            color=Pixel(0, 0, 0),
            hsync=False,
            vsync=False,
            vde=False,
            n_rst=False
        )

    @staticmethod
    def offscreen_signal(hsync: bool = False, vsync: bool = False) -> 'Signal':
        return Signal(
            color=Pixel.PURPLE(),
            hsync=hsync,
            vsync=vsync,
            vde=False,
            n_rst=True
        )

    @staticmethod
    def pixel_signal(color: Union[Pixel, Tuple[int,int,int]]) -> 'Signal':
        if isinstance(color, tuple):
            color = Pixel(r=color[0], g=color[1], b=color[2])

        # color is a Pixel always

        return Signal(
            color=color,
            hsync=False,
            vsync=False,
            vde=True,
            n_rst=True
        )

