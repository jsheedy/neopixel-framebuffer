from .fx import Fx


class YellowBlackAndRedGreenPurple(Fx):

    def _update(self):
        buff = self.video_buffer.buffer
        buff[:] = 0
        buff[0*3:20*3] = [255,255,0] * 20
        buff[20*3:40*3] = [0,0,0] * 20
        buff[40*3:60*3] = [255,0,0] * 20
        buff[60*3:80*3] = [0,255,0] * 20
        buff[80*3:100*3] = [102,51,153] * 20
