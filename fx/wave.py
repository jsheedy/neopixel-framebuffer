class Wave(object):

    pointer = itertools.cycle(range(N))

    buff = np.array( 255*np.sin(np.arange(0,420*N, dtype=np.uint8)) , dtype=np.uint8)

    def __init__(self, video_buffer, w=1, f=1):
        self.video_buffer = video_buffer
        self.w=w
        self.f=f

    def update(self):
        i = next(self.pointer)
        self.video_buffer.buffer = self.buff
        self.video_buffer.dirty = True

