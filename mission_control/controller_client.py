import zmq
from inputs import get_gamepad

def send_cmd(socket, speed, direction, EXIT=False):
    cmd = {
        'exit':EXIT,
        'speed':speed,
        'direction':direction,
    }
    socket.send_json(cmd)


def controller_client_process(port):

    context = zmq.Context()

    hostname = 'raspberrypi'
    socket = context.socket(zmq.PAIR)
    socket.connect(f"tcp://{hostname}:{port}")

    pressed = False
    direction = 0
    speed = 0
    MAX_RIGHT = 32767

    while True:
        events = get_gamepad()
        for event in events:
            if event.code == 'ABS_X' and speed != 0:
                direction2 = int(event.state / MAX_RIGHT * 100)
                if abs(direction2 - direction) > 5 or direction2 == 0:
                    direction = direction2
                    send_cmd(socket, speed, direction)

            if event.code == 'ABS_RZ':
                speed = event.state
                send_cmd(socket, speed, direction)

            elif event.code == 'ABS_Z':
                speed = -event.state
                send_cmd(socket, speed, direction)

            elif event.ev_type == 'Key' and event.code == 'BTN_START':
                send_cmd(socket, 0, 0, EXIT=True)
                socket.close()
                # socket.disable_monitor()
                break
