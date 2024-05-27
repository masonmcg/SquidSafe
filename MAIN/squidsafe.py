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
lcd.clear()

# Setup IMU stuff
from adafruit_bno08x import (BNO_REPORT_ROTATION_VECTOR)
from adafruit_bno08x.i2c import BNO08X_I2C
i2c = busio.I2C(board.SCL, board.SDA) # frequency=400000
bno = BNO08X_I2C(i2c, address=0x4B)  # Updated address to 0x4B
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

# Setup LED stuff
led = digitalio.DigitalInOut(board.D16)
led.direction = digitalio.Direction.OUTPUT

# Setup button stuff
blue_button = digitalio.DigitalInOut(board.D21)
blue_button.direction = digitalio.Direction.INPUT
red_button = digitalio.DigitalInOut(board.D20)
red_button.direction = digitalio.Direction.INPUT

# Setup variables
wheelie_angle = 20; # Wheelie angle in degrees


def enable_system():
	
	global wheelie_angle
    
    # Screen 1
	lcd.clear()
	lcd.message = "System enabled"
	lcd.message += "\nAngle: {:.2f}".format(wheelie_angle)
    
    # Sleep initially to avoid multiple button presses
	time.sleep(1)
    
	while True:
		
		for i in range(400):
			pitch_deg = get_pitch_angle()
			# Turn on the LED if pitch angle is above wheelie_angle
			if pitch_deg > wheelie_angle:
				led.value = True
			else:
				led.value = False
			time.sleep(0.0025)
        
		# If button pressed
		if blue_button.value or red_button.value:
			return


# Pings the IMU and returns pitch angle in degrees
def get_pitch_angle():
	
    # Read the quaternion data
    quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member

    # Convert to euler angles
    t2 = +2.0 * (quat_real * quat_j - quat_k * quat_i)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    # Convert radians to degrees
    pitch_deg = math.degrees(pitch)
    
    return pitch_deg


# Displays start screen and calls next function based on input
# Blue - change angle, Red - enable system
def start_screen():
	
	global wheelie_angle
	
	# Screen 1
	lcd.clear()
	lcd.message = "System disabled"
	lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
	
	# Sleep initially to avoid multiple button presses
	time.sleep(2)
	
	# Screen 2
	lcd.clear()
	lcd.message = "Blue - angle"
	lcd.message = "\nRed - enable"
	
	# Sleep initially to avoid multiple button presses
	time.sleep(2)
	
	while True:
	
		# Screen 1
		lcd.clear()
		lcd.message = "System disabled"
		lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
    
		# Wait 2 seconds while checking for button press
		for i in range(20):
			if blue_button.value:
				change_angle()
				# On return from change_angle, display screen 1
				# And sleep to avoid multiple button presses
				lcd.clear()
				lcd.message = "System disabled"
				lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
				time.sleep(1)
			elif red_button.value:
				enable_system()
				# On return from enable_ststem, display screen 1
				# And sleep to avoid multiple button presses
				lcd.clear()
				lcd.message = "System disabled"
				lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
				time.sleep(1)
			time.sleep(0.1)

		# Screen 2
		lcd.clear()
		lcd.message = "Blue - angle"
		lcd.message = "\nRed - enable"
    
		# Wait 2 seconds while checking for button press
		for i in range(20):
			if blue_button.value:
				change_angle()
				# On return from change_angle, display screen 1
				# And sleep to avoid multiple button presses
				lcd.clear()
				lcd.message = "System disabled"
				lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
				time.sleep(1)
			elif red_button.value:
				enable_system()
				# On return from enable_ststem, display screen 1
				# And sleep to avoid multiple button presses
				lcd.clear()
				lcd.message = "System disabled"
				lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
				time.sleep(1)
			time.sleep(0.1)
		
		
# Displays change angle screen and returns when angle is selected
def change_angle():
	
	global wheelie_angle
	timeout = 0  # Init timeout to 0 for selection ability
	
	# Screen 1
	lcd.clear()
	lcd.message = "Change angle: {:.2f}".format(wheelie_angle)
	lcd.message += "\nBlue+ Red- HOLD*"
	
	# Sleep initially to avoid multiple button presses
	time.sleep(1)
    
	while True:
		
		timeout = 0  # Init timeout to 0 for selection ability
        
        # If blue pressed, increment wheelie angle, display new angle
		if blue_button.value:
			wheelie_angle += 1
			lcd.clear()
			lcd.message = "Change angle: {:.2f}".format(wheelie_angle)
			lcd.message += "\nBlue+ Red- HOLD*"
            
            # Wait until blue unpressed to move on
            # Or if reach timeout, consider the angle to be selected
            # And then return with that angle set
			while blue_button.value:
				timeout += 1
				if timeout > 20: 
					wheelie_angle -= 1
					return
				time.sleep(0.1)
        
        # If red pressed, decrement wheelie angle, display new angle
		elif red_button.value:
			wheelie_angle -= 1
			lcd.clear()
			lcd.message = "Change angle: {:.2f}".format(wheelie_angle)
			lcd.message += "\nBlue+ Red- HOLD*"
            
            # Wait until red unpressed to move on
            # Or if reach timeout, consider the angle to be selected
            # And then return with that angle set
			while red_button.value:
				timeout += 1
				if timeout > 20: 
					wheelie_angle += 1
					return
				time.sleep(0.1)
        
        # Sleep to not do stuff constantly
		time.sleep(0.05)


# Start logic
start_screen()
