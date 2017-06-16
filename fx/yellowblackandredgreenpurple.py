import itertools
from .fx import Fx


class YellowBlackAndRedGreenPurple(Fx):

    _colors = (
        [255,255,0] * 20,
        [0,0,0] * 20,
        [255,0,0] * 20,
        [0,255,0] * 20,
        [102,51,153] * 20
    )

    def __init__(self, *args, width=20, start_indexes=(0, 105, 210, 320),**kwargs):
        super().__init__(*args, **kwargs)
        slices = [
            slice((x + i*width)*3,(x + (i+1)*width)*3)
            for x in start_indexes
            for i in range(len(self._colors))
        ]
        self._slice_colors = list(zip(slices, itertools.cycle(self._colors)))

    def _update(self):
        for slice, color in self._slice_colors:
            self.video_buffer.buffer[slice] = color
