import zmq
import GUI
import numpy as np
import cv2
import json
import tensorflow as tf


def mp_process(port):

    context = zmq.Context()

    hostname = 'raspberrypi'

    print(f"Connecting to server on port {port}...")
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{hostname}:{port}")

    model = load_model()
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    temp, img_ = GUI.start()

    while True:

        try:
            message = socket.recv()
        except:
            socket.close()
            break

        if message[:3] == b'cam':
            message = message[4:]

            img = np.frombuffer(message, dtype=np.uint8)
            img = np.reshape(img, (240, 320, 3))
            img = detect(model, img)
            img_[:] = list(img)

            t = np.random.normal(18, 0.1)
            temp.pop(0)
            temp.append(t)

        if message[:4] == 'temp':
            _, t, h = message.split()
            temp.pop(0)
            temp.append(float(t))

def load_model():
    import tensorflow_hub

    print("loading model...")

    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    model = tensorflow_hub.load("https://tfhub.dev/tensorflow/efficientdet/d0/1")

    print("model load finished  ")

    return model

def detect(model, img, thres=0.5):

    cats = json.loads(open("../coco.json").read())
    cats = {v['id']: v['name'] for v in cats['categories']}

    image_tensor = tf.convert_to_tensor(img)
    image_tensor = tf.expand_dims(image_tensor, 0)

    detector_output = model(image_tensor)
    height, width = img.shape[:2]

    for i in range(int(detector_output['num_detections'][0].numpy())):
        score = detector_output['detection_scores'][0][i].numpy()
        if score > thres:
            box = detector_output['detection_boxes'][0, i, :]

            ymin, xmin, ymax, xmax = box.numpy()

            xmin *= width
            xmax *= width
            ymin *= height
            ymax *= height

            img = cv2.rectangle(np.array(img), (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 3)

            cat = cats[detector_output['detection_classes'][0][i].numpy()]
            cv2.putText(img, cat, (int(xmin + 5), int(ymin + 15)), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

    return img
