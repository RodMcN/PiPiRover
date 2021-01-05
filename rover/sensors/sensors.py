from . import dht, camera
import time
import asyncio
import zmq


def startup(port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{port}")

    asyncio.run(run(socket))

async def camera_capture(cam):
    img = cam.capture()
    #return ["cam", "img"]
    return b'cam ' + img.tobytes()

async def temp_read(sensor):
    t, h = sensor.capture()
    return ["temp", str(t), str(h)]

async def run(socket):

    cam = camera.Camera()
    ts = dht.DHT()

    # tasks = [camera_capture(cam), temp_read()]
    # for while True:
    #     finished, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    #     result = finished.pop().result()
    #     print(result[0], tasks)

    
    try:
        while True:
            result = await camera_capture(cam)
            socket.send(result)
            time.sleep(0.5)
            result = await temp_read(ts)
            socket.send_string(" ".join(result))

    finally:
        cam.stop()
        socket.close()

#asyncio.run(run())