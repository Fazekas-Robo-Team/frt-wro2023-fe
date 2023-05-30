
from fastapi import FastAPI, Response, Request, HTTPException, Form, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import io
import logging

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

import cv2
import numpy as np
import time
import base64
import os


api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Config:
    cut_frame_height = 40
    full_resolution = (1536, 160)
    fov = 70.42
    opencv_threads = 1
    picamera2_threads = 2
    framerate = 30


class Stats:
    pass


def reset_stats():
    Stats.frames = 0
    Stats.start_time = time.time()
    Stats.skipped_frames = 0


lock = False


class Frame:
    def __init__(self):
        self.full_jpeg = None
        self.red_mask_jpeg = None
        self.green_mask_jpeg = None
        self.contours_jpeg = None


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = Frame()
        self.subscribers: dict[str, list[Frame]] = {}
        self.condition = asyncio.Condition()

    async def _write(self, buf):
        async with self.condition:
            process_frame(buf)
            for frames in self.subscribers.values():
                frames.append(self.frame)
            self.condition.notify_all()

    def write(self, buf):
        if not lock:
            loop.create_task(self._write(buf))
        else:
            Stats.skipped_frames += 1

    def subscribe(self):
        # generate random key
        key = base64.b64encode(os.urandom(32)).decode('utf-8')
        self.subscribers[key] = []
        return key
    
    def unsubscribe(self, key):
        del self.subscribers[key]

    async def get_frame(self, key):
        if len(self.subscribers[key]) == 0:
            async with self.condition:
                await self.condition.wait()
        frame = self.subscribers[key].pop(0)
        if len(self.subscribers[key]) > Config.framerate:
            self.subscribers[key].clear()
        return frame


@api.on_event("startup")
async def startup():
    global loop
    loop = asyncio.get_running_loop()

    global cam
    cam = Picamera2()

    global cam_output
    cam_output = StreamingOutput()
    apply_settings()
    reset_stats()


def apply_settings ():
    try:
        cam.stop_recording()
    except:
        pass
    config = cam.create_video_configuration(
        main = {
            "size": Config.full_resolution,
        },
        controls = {
            "FrameRate": Config.framerate,
        },
        #buffer_count = 3,
        #queue = False,
    )
    cam.align_configuration(config)
    cam.configure(config)
    cam.start_recording(JpegEncoder(num_threads = Config.picamera2_threads), FileOutput(cam_output))

    cv2.setNumThreads(Config.opencv_threads)


def process_frame(raw_jpeg):
    global lock
    lock = True

    frame = cv2.imdecode(np.frombuffer(raw_jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
    top = frame.shape[0] // 2 - Config.cut_frame_height // 2
    bottom = frame.shape[0] // 2 + Config.cut_frame_height // 2

    section = frame[top:bottom, :, :]

    blurred = cv2.GaussianBlur(section, (3, 3), 0)

    # H [0, 360], S [0, 100], V [0, 100]
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Define lower and upper ranges for red color
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Create mask for red color
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        bounding_rect = cv2.boundingRect(largest_contour)
        cv2.rectangle(blurred, bounding_rect, (0, 255, 0), 1)

    # Define range of green color in HSV
    lower_green = np.array([70, 30, 30])
    upper_green = np.array([90, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green,)

    contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        bounding_rect = cv2.boundingRect(largest_contour)
        cv2.rectangle(blurred, bounding_rect, (0, 255, 0), 1)

    # downscale frame to quarter size
    small_full = cv2.resize(frame, (0, 0), fx=0.125, fy=0.125)
    small_red_mask = cv2.resize(red_mask, (0, 0), fx=0.25, fy=0.25)
    small_green_mask = cv2.resize(green_mask, (0, 0), fx=0.25, fy=0.25)
    small_contours = cv2.resize(blurred, (0, 0), fx=0.25, fy=0.25)
    
    small_full_jpeg = cv2.imencode('.jpg', small_full)[1].tobytes()
    small_red_mask_jpeg = cv2.imencode('.jpg', small_red_mask)[1].tobytes()
    small_green_mask_jpeg = cv2.imencode('.jpg', small_green_mask)[1].tobytes()
    small_contours_jpeg = cv2.imencode('.jpg', small_contours)[1].tobytes()

    cam_output.frame.full_jpeg = base64.b64encode(small_full_jpeg).decode('utf-8')
    cam_output.frame.red_mask_jpeg = base64.b64encode(small_red_mask_jpeg).decode('utf-8')
    cam_output.frame.green_mask_jpeg = base64.b64encode(small_green_mask_jpeg).decode('utf-8')
    cam_output.frame.contours_jpeg = base64.b64encode(small_contours_jpeg).decode('utf-8')

    # updating stats
    Stats.frames += 1

    lock = False


@api.websocket('/stream/{name}')
async def stream(websocket: WebSocket, name: str):
    await websocket.accept()
    key = cam_output.subscribe()

    while websocket.client_state != 2:
        frame = await cam_output.get_frame(key)

        try:
            jpeg = getattr(frame, name + '_jpeg')
        except AttributeError:
            websocket.close(reason = "Invalid stream name")

        if frame is None:
            continue

        await websocket.send_text(jpeg)

    cam_output.unsubscribe(key)


@api.post('/settings')
async def settings_post(
    width: int = Form(),
    height: int = Form(),
    fov: str = Form(),
    cut_frame_height: int = Form(),
    opencv_threads: int = Form(),
    picamera2_threads: int = Form(),
    framerate: int = Form(),
):
    Config.full_resolution = (width, height)
    Config.fov = float(fov)
    Config.cut_frame_height = cut_frame_height
    Config.opencv_threads = opencv_threads
    Config.picamera2_threads = picamera2_threads
    Config.framerate = framerate
    apply_settings()


@api.get('/stats')
async def stats():
    try:
        return {
            "avg_fps": round(Stats.frames / (time.time() - Stats.start_time), 2),
            "skipped_frames": Stats.skipped_frames,
            "skipped_frames_percent": round(Stats.skipped_frames / (Stats.frames + Stats.skipped_frames) * 100, 2),
        }
    except:
        pass

@api.post('/reset_stats')
async def reset_stats_post():
    reset_stats()
