from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse

from api.cam import gen

api = FastAPI()

@api.get('/')
async def index(request: Request):
    return "Hello World!"

@api.get('/stream.mjpeg')
async def stream(request: Request):
    return StreamingResponse(gen(), media_type='multipart/x-mixed-replace; boundary=frame')
