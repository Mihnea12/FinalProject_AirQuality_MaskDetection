import time
from gpiozero import OutputDevice
GPIO_PIN = 17

fan = OutputDevice(GPIO_PIN)
fan.value = 0
i = 0
while True:
    if i < 5:
        fan.on()
        i = i + 1
        time.sleep(1)
    print(i)
    if i == 5:
        fan.off()
        print("test")
    
    time.sleep(1)
    
    
    
    