import zmq
from multiprocessing import Process
import message_processor, controller_client

if __name__ == '__main__':

    context = zmq.Context()

    hostname = 'raspberrypi'
    port = '5555'

    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{hostname}:{port}")
    socket.send(bytes("sensors", "utf-8"))
    port = socket.recv().decode("utf-8")
    print("received", port)
    Process(target=message_processor.mp_process, args=(port,)).start()

    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{hostname}:{port}")
    socket.send(bytes("motors", "utf-8"))
    port = socket.recv().decode("utf-8")
    print("received", port)
    Process(target=controller_client.controller_client_process, args=(port,)).start()


# TODO 