import time
import board
import busio
import math

from adafruit_bno08x import (
    # BNO_REPORT_ACCELEROMETER,
    # BNO_REPORT_GYROSCOPE,
    # BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)

from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
bno = BNO08X_I2C(i2c, address=0x4B)  # Updated address to 0x4B

# bno.enable_feature(BNO_REPORT_ACCELEROMETER)
# bno.enable_feature(BNO_REPORT_GYROSCOPE)
# bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

while True:
    time.sleep(0.5)
    # print("Acceleration:")
    # accel_x, accel_y, accel_z = bno.acceleration  # pylint:disable=no-member
    # print("X: %0.6f  Y: %0.6f Z: %0.6f  m/s^2" % (accel_x, accel_y, accel_z))
    # print("")

    # print("Gyro:")
    # gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
    # print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))
    # print("")

    # print("Magnetometer:")
    # mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
    # print("X: %0.6f  Y: %0.6f Z: %0.6f uT" % (mag_x, mag_y, mag_z))
    # print("")

    # print("Rotation Vector Quaternion:")
    # quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member
    # print("I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quat_i, quat_j, quat_k, quat_real))
    # print("")
    
    # Read the quaternion data
    quat_i, quat_j, quat_k, quat_real = bno.quaternion  # pylint:disable=no-member

    # Convert the quaternion to Euler angles
    ysqr = quat_j * quat_j

    t0 = +2.0 * (quat_real * quat_i + quat_j * quat_k)
    t1 = +1.0 - 2.0 * (quat_i * quat_i + ysqr)
    roll = math.atan2(t0, t1)

    t2 = +2.0 * (quat_real * quat_j - quat_k * quat_i)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    t3 = +2.0 * (quat_real * quat_k + quat_i * quat_j)
    t4 = +1.0 - 2.0 * (ysqr + quat_k * quat_k)
    yaw = math.atan2(t3, t4)

    # Convert radians to degrees
    roll_deg = math.degrees(roll)
    pitch_deg = math.degrees(pitch)
    yaw_deg = math.degrees(yaw)

    # Print the Euler angles
    print("Euler Angles:")
    print("Roll: %0.6f  Pitch: %0.6f  Yaw: %0.6f degrees" % (roll_deg, pitch_deg, yaw_deg))
    print("")
