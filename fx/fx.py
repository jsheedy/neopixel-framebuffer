class Fx(object):
    enabled = True

    def __init__(self, video_buffer, enabled=True):
        self.video_buffer = video_buffer
        self.enabled = enabled

    def update(self):
        if not self.enabled:
            return

    def toggle(self):
        self.enabled = not self.enabled