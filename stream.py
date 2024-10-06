import os
from picamera2 import Picamera2
from PIL import Image, ImageDraw, ImageFont
import time
import LCD_1in44

frames_per_sec = 24
frame_delay = 1.0 / frames_per_sec
print(f"Frame delay: {frame_delay}")

# Setup display
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Set correct LCD dimensions (128x128)
lcd_width = 128
lcd_height = 128

# Setup the camera in low-res mode initially
try:
    picam2 = Picamera2(0)  # Explicitly specify camera 0
    #low_res_config = picam2.create_preview_configuration(main={"size": (320, 240)})  # Start in low-res mode
    low_res_config = picam2.create_preview_configuration(main={"size": (lcd_width, lcd_height)})
    picam2.configure(low_res_config)
except Exception as e:
    print(f"Error initializing camera: {e}")
    raise

# Create directory if it doesn't exist
image_dir = "images/"
os.makedirs(image_dir, exist_ok=True)

# Start the camera
picam2.start()
print("Camera started in low-res mode and streaming to the 1.44-inch LCD")

image_counter = 0

# Create a font for the "Picture Taken" message
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except IOError:
    font = ImageFont.load_default()

def draw_picture_taken_message(img):
    draw = ImageDraw.Draw(img)
    message = "Picture Taken"
    textwidth, textheight = draw.textsize(message, font)
    x = (lcd_width - textwidth) // 2
    y = (lcd_height - textheight) // 2
    draw.rectangle((x-5, y-5, x+textwidth+5, y+textheight+5), fill=(0, 0, 0))
    draw.text((x, y), message, font=font, fill=(255, 255, 255))
    return img

img_exposure_time = 25000
live_exposure_time = 45000

picam2.set_controls({"ExposureTime": live_exposure_time})

try:
    picture_taken_time = None
    while True:
        start_time = time.time()
        # Capture camera image
        frame = picam2.capture_array()

        # Convert numpy array (frame) to image
        img = Image.fromarray(frame)

        # Resize the image to match the LCD dimensions
        #img = img.resize((lcd_width, lcd_height), Image.LANCZOS)

        # Rotate the image 90 degrees clockwise
        img = img.rotate(-90)

        # Check if KEY1 is pressed to switch to high-res, save the image, and switch back
        if disp.digital_read(disp.GPIO_KEY1_PIN) != 0:  # If the key is pressed
            # Stop the camera before reconfiguring
            picam2.stop()

            # Switch to high-resolution mode
            hires_width = 2592
            hires_height = 1944
            high_res_config = picam2.create_still_configuration(main={"size": (hires_width, hires_height)})  # Switch to high-res
            picam2.configure(high_res_config)
            """
            picam2.start()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            zfilled_counter = str(image_counter).zfill(6)
            image_path = os.path.join(image_dir, f"{zfilled_counter}_{timestamp}.jpg")
            picam2.capture_file(image_path)
            image_counter += 1
            picam2.stop()
            """
            picam2.set_controls({"ExposureTime": img_exposure_time})  # Set exposure time to 5ms
            picam2.start()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            zfilled_counter = str(image_counter).zfill(6)
            image_path = os.path.join(image_dir, f"{zfilled_counter}_{timestamp}.jpg")
            # Capture a high-resolution image
            picam2.capture_file(image_path)
            print(f"Saved high-resolution image to {image_path}")
            image_counter += 1
            picture_taken_time = time.time()
            print("Button pressed: KEY1")

            # Stop the camera again before switching back
            picam2.stop()

            # Switch back to low-resolution mode
            picam2.configure(low_res_config)
            picam2.set_controls({"ExposureTime": live_exposure_time})  # Set exposure time to 5ms
            picam2.start()

        # If picture was taken less than 3 seconds ago, show the message
        if picture_taken_time and time.time() - picture_taken_time < 3:
            img = draw_picture_taken_message(img)

        # Convert to RGB for display
        img = img.convert('RGB')

        # Display the image on the LCD
        disp.LCD_ShowImage(img, 0, 0)

        # Print messages for other button presses
        buttons = [
            (disp.GPIO_KEY_UP_PIN, "Up"),
            (disp.GPIO_KEY_DOWN_PIN, "Down"),
            (disp.GPIO_KEY_LEFT_PIN, "Left"),
            (disp.GPIO_KEY_RIGHT_PIN, "Right"),
            (disp.GPIO_KEY_PRESS_PIN, "Center"),
            (disp.GPIO_KEY2_PIN, "KEY2"),
            (disp.GPIO_KEY3_PIN, "KEY3")
        ]
        
        for pin, name in buttons:
            if disp.digital_read(pin) != 0:  # If the key is pressed
                print(f"Button pressed: {name}")

        #time.sleep(frame_delay)
        end_time = time.time()
        elapsed_time = end_time - start_time
        delta_t = frame_delay - elapsed_time
        if delta_t > 0:
            time.sleep(delta_t)
        else:
            print(f"Frame took longer than {frame_delay} seconds: {elapsed_time} seconds")

except KeyboardInterrupt:
    print("Camera stream interrupted.")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    picam2.close()
    disp.LCD_Clear()
    print("Camera closed and display cleared")
