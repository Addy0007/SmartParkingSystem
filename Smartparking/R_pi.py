import time
import subprocess
import owncloud
import RPi.GPIO as GPIO
import socket

# ownCloud setup
oc = owncloud.Client('http://192.168.1.16/owncloud')
oc.login('siddhant', 'qwertyuiop')

# GPIO setup
IR_PIN = 18  # Adjust the GPIO pin number
SERVO_PIN = 17  # Adjust the GPIO pin number for the servo motor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Function to capture image using libcamera-jpeg
def capture_image():
    image_path = "/home/siddhant/pyocclient/entry.png"
    subprocess.run(["libcamera-jpeg", "-o", image_path])
    print(f"Image captured: {image_path}")
    return image_path

# Function to open the servo gate by 90 degrees
def open_servo_gate():
    pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM frequency
    pwm.start(7.5)  # Initial servo position

    duty = 90 / 18 + 2  # Map angle (90 degrees) to duty cycle (2 to 12)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)  # Wait for the servo to reach the desired position
    pwm.stop()

# Function to reset the servo to 0 degrees
def reset_servo():
    pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM frequency
    pwm.start(7.5)  # Initial servo position
    pwm.ChangeDutyCycle(2)  # Move servo to 0 degrees
    time.sleep(1)  # Wait for the servo to reach the desired position
    pwm.stop()

# Socket setup
HOST = '192.168.1.16'  # Laptop's IP address
PORT = 45880

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))

try:
    while True:
        # Wait for the IR sensor to be activated
        print("Waiting for IR sensor to be activated...")
        while GPIO.input(IR_PIN) == GPIO.HIGH:
            time.sleep(0.1)

        # IR sensor activated, start the loop
        print("IR sensor activated. Starting the loop...")

        # Capture image and upload to ownCloud
        image_path = capture_image()
        oc.put_file('testdir/entry.png', image_path) 
        print("File uploaded to ownCloud")

        # Wait for a message from the laptop
        print("Waiting for a message from the laptop...")
        data, addr = sock.recvfrom(1024)
        received_number = data.decode()
        print("Received number:", received_number)

        # Open the servo gate
        open_servo_gate()

        # Wait for the IR sensor to detect an object
        while GPIO.input(IR_PIN) == GPIO.LOW:
            time.sleep(0.1)
        time.sleep(5)

        # Close the servo gate
        reset_servo()
except KeyboardInterrupt:
    print("Keyboard interrupt detected. Exiting...")
finally:
    print("Closing the socket...")
    sock.close()  # Close the socket
    print("Socket closed.")
    GPIO.cleanup()  # Clean up GPIO resources
