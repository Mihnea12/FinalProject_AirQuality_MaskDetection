import math
import pyfirmata
import time
import requests
import RPi.GPIO as GPIO
from gpiozero import OutputDevice

GPIO_PIN = 17
fan = OutputDevice(GPIO_PIN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 12 to be an input pin and set initial value to be pulled low (off)
GPIO.setwarnings(False) # Ignore warning for now

fan_value = "False"
correctedPPM = 0
manual_fan = 0
co2Zero = 55

def map(x,in_min,in_max,out_min,out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/ttyUSB0')
    print("Communication Successfully started")

    it = pyfirmata.util.Iterator(board)
    it.start()

    gas_sensor = board.analog[0]
    gas_sensor.enable_reporting()
    co2now = [0,0,0,0,0,0,0,0,0,0]
    zzz = 0
    while True:
        zzz = 0
        value = gas_sensor.read()
        if value and value * 100: 
            for i in range(0, 10, 1):
                value = gas_sensor.read()
                co2now[i] = map(value, 0, 1.0, 0, 1023)
                time.sleep(0.2)
            print(co2now)
            for i in range(0, 10, 1):
                zzz = zzz + co2now[i]
            co2raw = zzz/20
            co2comp = co2raw - co2Zero
            aqi = co2comp
            co2ppm = map(co2comp, 0, 1023, 400, 5000)

            if GPIO.input(18) == GPIO.HIGH:
                if manual_fan == 0:
                    manual_fan = 1
                elif manual_fan == 1:
                    manual_fan = 0
                time.sleep(2)
            if manual_fan == 0:
                if value < 5:
                    value = 15
                if (co2ppm > 1000 or aqi > 100 ) and not fan.value:
                    fan.on()
                    fan_value = "True"
                elif fan.value and (co2ppm <= 1000 and aqi <= 100 ):
                    fan.off()
                    fan_value = "False"
            else:
                manual_fan = 1
                fan.on()
                fan_value = "True"
            
            requests.post("http://localhost:5000/data", data={'co2':round(co2ppm), 'aqi': round(aqi), 'fan': fan_value})
            print("\n Value AQI: %s" % round(aqi))
            print("Corrected PPM: %s ppm" % round(co2ppm))
        time.sleep(20)
   
            