import time
import board
import adafruit_dht
    
class DHT():
    def __init__(self, pin=26):
        self.device = adafruit_dht.DHT11(eval(f"board.D{pin}"))
    
    def capture(self):
        try:
            temperature = self.device.temperature
            humidity = self.device.humidity
            return temperature, humidity
        except RuntimeError:
            return None, None

    def stop(self):
        self.device.exit()