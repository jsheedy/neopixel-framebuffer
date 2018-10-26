import itertools
from .fx import Fx


class YellowBlackAndRedGreenPurple(Fx):

    _colors = (
        [1,1,0],
        [0,0,0],
        [1,0,0],
        [0,1,0],
        [.4,.2,.6]
    )

    def __init__(self, *args, start_points=(0, .2, .5, .75),**kwargs):
        super().__init__(*args, **kwargs)
        slices = []
        width = int(self.N / len(start_points) / 5)
        for x in start_points:
            for i in range(len(self._colors)):
                idx = int(self.N * x)
                slices.append(slice((idx + i*width),(idx + (i+1)*width)))

        self._slice_colors = list(zip(slices, itertools.cycle(self._colors)))

    def _update(self):
        self.x[:] = 0
        for slice, color in self._slice_colors:
            self.x[slice,:] = color

        return self.x
