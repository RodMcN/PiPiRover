import picamera
import numpy as np


class Camera():
    def __init__(self, resolution=(320, 240), framerate=24):
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate

    def capture(self):
        # IOStream?
        output = np.empty((*self.camera.resolution, 3), dtype=np.uint8)
        self.camera.capture(output, 'rgb')
        return output

    def stop(self):
        self.camera.close()
