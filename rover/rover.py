from sensors import sensors
import motors
import zmq
from multiprocessing import Process

sensors_running = False
motors_running = False

if __name__ == "__main__":

    while True:

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        message = socket.recv()

        try:
            message = message.decode("utf-8")
            print(message)
            if message == 'sensors':
                port = 5678
                socket.send(bytes(str(port), "utf-8"))

                if not sensors_running:
                    p = Process(target=sensors.startup, args=(port,))
                    p.start()
                    sensors_running = True

            if message == "motors":
                if sensors_running:
                    socket.send(bytes("motors already in use"), "utf-8")
                else:
                    port = 5432
                    socket.send(bytes(str(port), "utf-8"))
                    p = Process(target=motors.motors_process, args=(port,))
                    p.start()
                    motors_running = True # TODO switch back when disconnect

        except Exception as e:
            print(e)

        finally:
            socket.close()
            break
