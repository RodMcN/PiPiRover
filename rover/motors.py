import zmq
import json
import RPi.GPIO as gpio

MAX_LEFT = -32768
MAX_RIGHT = 32767

def gpio_setup(pins):

    gpio.setmode(gpio.BOARD)
    gpio.setup(pins['left_forward'], gpio.OUT)
    gpio.setup(pins['left_reverse'], gpio.OUT)
    gpio.setup(pins['right_forward'], gpio.OUT)
    gpio.setup(pins['right_reverse'], gpio.OUT)

    gpio.setup(pins['left_power'], gpio.OUT)
    gpio.setup(pins['right_power'], gpio.OUT)

    gpio.output(pins['left_forward'], False)
    gpio.output(pins['left_reverse'], False)
    gpio.output(pins['right_forward'], False)
    gpio.output(pins['right_reverse'], False)

    '''
    Software PWM available on all pins
    Hardware PWM available on GPIO12, GPIO13, GPIO18, GPIO19
    '''



def forward(pins):
    gpio.output(pins['left_reverse'], False)
    gpio.output(pins['right_reverse'], False)
    gpio.output(pins['left_forward'], True)
    gpio.output(pins['right_forward'], True)

def reverse(pins):
    gpio.output(pins['left_forward'], False)
    gpio.output(pins['right_forward'], False)
    gpio.output(pins['left_reverse'], True)
    gpio.output(pins['right_reverse'], True)

def motors_process(port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(f"tcp://*:{port}")
    
    pins = json.loads(open("pins.json").read())['motors']

    gpio_setup(pins)

    p_left = gpio.PWM(pins['left_power'], 1000)
    p_right = gpio.PWM(pins['right_power'], 1000)
    pressed = False

    while True:
        msg = socket.recv()
        msg = json.loads(msg)

        if msg['exit'] == True:
            socket.close()
            break

        direction = msg['direction']
        speed = msg['speed']
        if speed == 0:
            gpio.output(pins['left_forward'], False)
            gpio.output(pins['right_forward'], False)
            p_left.stop()
            p_right.stop()
            pressed = False

        else:
            speed = int(speed) / 255
            right_motor = abs(min(100, 100 - direction) * speed)
            left_motor = abs(min(100, 100 + direction) * speed)
            if not pressed:
                if speed >= 0:
                    forward(pins)
                else:
                    reverse(pins)
                p_left.start(left_motor)
                p_right.start(right_motor)
                pressed = True
            else:
                p_left.ChangeDutyCycle(left_motor)
                p_right.ChangeDutyCycle(right_motor)

    gpio.cleanup()  

