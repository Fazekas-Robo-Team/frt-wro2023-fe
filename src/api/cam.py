import cv2
import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

from threading import Condition
import io
import asyncio
import uvloop

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main = {
        "size": (800, 400),
    },
)
picam2.align_configuration(config)
picam2.configure(config)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = asyncio.Condition()

    async def _write(self, buf):
        async with self.condition:
            self.frame = buf
            self.condition.notify_all()

    def write(self, buf):
        asyncio.get_event_loop_policy().get_event_loop().create_task(self._write(buf))
            

output = StreamingOutput()
picam2.start_recording(JpegEncoder(num_threads = 3), FileOutput(output))

async def gen():
    while True:
        async with output.condition:
            await output.condition.wait()
            frame = output.frame

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
