import serial
import time

def keypress():
     
     ser = serial.Serial('COM11', 2400, timeout=1)

     time.sleep(2)  # wait for Arduino reset

     while True:
      if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        sensor1 = data.split(":")[0]
        sensor2 = data.split(":")[1]

        if int(sensor1) > 10000 and int(sensor2) > 10000:
            print("sensors 3 triggered")
            # pyautogui.press('down')  # Simulate pressing the 'Down Arrow' key

        elif int(sensor1) > 10000:
            print("Sensor 1 triggered")
            # pyautogui.press('delete')  # Simulate pressing the 'Delete' key
        
        elif int(sensor2) > 10000:
            print("Sensor 2 triggered")
            # pyautogui.press('enter')  # Simulate pressing the 'Enter' key

            

keypress()