import time
import board
import busio
import math
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# Setup LCD stuff
lcd_columns = 16
lcd_rows = 2
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d4 = digitalio.DigitalInOut(board.D13)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d7 = digitalio.DigitalInOut(board.D0)
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# Setup IMU stuff
from adafruit_bno08x import (BNO_REPORT_ROTATION_VECTOR)
from adafruit_bno08x.i2c import BNO08X_I2C
i2c = busio.I2C(board.SCL, board.SDA) # frequency=400000
bno = BNO08X_I2C(i2c, address=0x4B)  # Updated address to 0x4B
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

# Setup LED stuff
led = digitalio.DigitalInOut(board.D16)
led.direction = digitalio.Direction.OUTPUT

while True:
    time.sleep(0.1)
    
    # Read the quaternion data
    quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member

    # Convert to euler angles
    t2 = +2.0 * (quat_real * quat_j - quat_k * quat_i)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    # Convert radians to degrees
    pitch_deg = math.degrees(pitch)

    lcd.clear()
    lcd.message = "Angle: {:.2f}".format(pitch_deg)
    
     # Turn on the LED if yaw angle is above 20 degrees
    if pitch_deg > 20:
        led.value = True
        lcd.message = "\nLED ON"
    else:
        led.value = False
        lcd.message = "\nLED OFF"
        
    
