class Fx(object):
    enabled = True

    def __init__(self, video_buffer):
        self.video_buffer = video_buffer
        self.enabled = True

    def update(self):
        if not self.enabled:
            return

    def toggle(self):
        self.enabled = not self.enabled