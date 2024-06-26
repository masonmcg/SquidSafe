import subprocess
import gpiod
import time
import board
import digitalio
import atexit
import busio
import math
import adafruit_character_lcd.character_lcd as characterlcd

"""
NOTES:
display current angle on disabled screen, also incorporate exact angle offset
also maybe include calibration on the disabled screen as well

need faster switching, maybe try to get raw angle data and use that instead of corrected data

also probably need faster switching relay as well

also add new pins and stuff to the pinout schematic file

also fix the weird stuff in the start screen loop and just have a mian loop that does everything
"""

# Sleep to let other start stuff happen
time.sleep(1)

# Function to forcefully reset specified GPIO pins using libgpiod
def reset_gpio_pins():
    chip = gpiod.Chip('gpiochip0')
    for line in chip.get_all_lines():
        try:
            line.release()
        except OSError as e:
            print(f"Error releasing pin {line.offset()}: {e}")

# Reset GPIO pins at the start of the program
reset_gpio_pins()

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
led_red = digitalio.DigitalInOut(board.D16)
led_red.direction = digitalio.Direction.OUTPUT
led_blue = digitalio.DigitalInOut(board.D12)
led_blue.direction = digitalio.Direction.OUTPUT

# Setup button stuff
blue_button = digitalio.DigitalInOut(board.D21)
blue_button.direction = digitalio.Direction.INPUT
red_button = digitalio.DigitalInOut(board.D20)
red_button.direction = digitalio.Direction.INPUT

# Setup spark cut relay stuff
spark = digitalio.DigitalInOut(board.D18)
spark.direction = digitalio.Direction.OUTPUT
spark.value = True

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
	
	# File recorder stuff
	"""
	f = open("/home/mason/Desktop/CPE542/SquidSafe/MAIN/angle_log.txt","a")
	last_time_us = None
	"""
	
	while True:
		
		led_blue.value = True
		
		for i in range(400):
			pitch_deg = get_pitch_angle()
			
			# File recorder stuff
			"""
			# Get the current time in microseconds
			current_time_us = int(time.time() * 1_000_000)

			if last_time_us is None:
				elapsed_time_us = 0  # For the first entry, elapsed time is 0
			else:
				elapsed_time_us = current_time_us - last_time_us

			# Write the timestamp, elapsed time, and angle to the file
			f.write(f"{current_time_us}, {elapsed_time_us}, {pitch_deg:.2f}\n")

			# Update last_time_us to the current time
			last_time_us = current_time_us
			"""
			
			# Turn on the LED if pitch angle is above wheelie_angle
			if pitch_deg > wheelie_angle:
				led_red.value = True
				spark.value = False
			else:
				led_red.value = False
				spark.value = True
			time.sleep(0.002)
		
		# If button pressed
		if blue_button.value or red_button.value:
			# File recorder stuff
			"""
			f.close()
			"""
			spark.value = True
			led_blue.value = False
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
    
    return -pitch_deg


# Displays start screen and calls next function based on input
# Blue - change angle, Red - enable system
def start_screen():
	
	global wheelie_angle
	
	# Screen 1
	lcd.clear()
	lcd.message = "System disabled"
	lcd.message = "\nAngle: {:.2f}".format(wheelie_angle)
	
	# Sleep initially to avoid multiple button presses
	time.sleep(1)
	
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
			
		# Screen 3
		lcd.clear()
		lcd.message = "Current angle"
		lcd.message += "\n{:.2f} degrees".format(get_pitch_angle())

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
		

# Does all this on program exit for any reason
# Releases all gpio pins except for the spark one, it keeps that on
def exit_stuff():
	reset_gpio_pins()
	# Setup spark cut relay stuff
	spark = digitalio.DigitalInOut(board.D18)
	spark.direction = digitalio.Direction.OUTPUT
	spark.value = True
	
# Ensure GPIO pins are reset at program exit and spark on
atexit.register(exit_stuff)

# Start logic
start_screen()
