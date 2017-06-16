from .fx import Fx


class YellowBlackAndRedGreenPurple(Fx):

    colors = (
        [255,255,0] * 20,
        [0,0,0] * 20,
        [255,0,0] * 20,
        [0,255,0] * 20,
        [102,51,153] * 20
    )

    width = 20
    # list(zip(range(6), itertools.cycle(range(3))))

    def _update(self):
        for start_index in (0, 105, 210, 320):
            for i, color in enumerate(self.colors):
                self.video_buffer.buffer[(start_index + i*self.width)*3:(start_index + (i+1)*self.width)*3] = color
