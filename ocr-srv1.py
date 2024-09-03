import pytesseract
from PIL import ImageGrab
from PIL import ImageEnhance, Image
import pyttsx3
import ctypes
import time
import keyboard
import win32gui
import win32api
import win32con

# Set the Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define thresholds for merging text boxes
HORIZONTAL_THRESHOLD = 27  # Horizontal distance in pixels to merge text boxes
VERTICAL_THRESHOLD = 1  # Vertical distance in pixels to merge text boxes

scanning_active = False
last_text = ""
boxes = []
timer_active = False
paused = False  # New variable to track pause state
reading_text = False  # New variable to track if text is being read

abc = False

def capture_screen():
    # Capture the entire screen
    return ImageGrab.grab()

def perform_ocr_with_positions(image):
    # Perform OCR and get bounding boxes for each piece of detected text
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return data

def get_mouse_position():
    # Get the current mouse position
    pt = ctypes.windll.user32.GetCursorPos

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    point = POINT()
    pt(ctypes.byref(point))
    return point.x, point.y

def merge_text_boxes(data):
    # Merge adjacent text boxes based on the defined thresholds
    boxes = []
    n_boxes = len(data['level'])

    for i in range(n_boxes):
        (left, top, width, height, text) = (
            data['left'][i], data['top'][i], data['width'][i], data['height'][i], data['text'][i])
        if text.strip():  # Only process non-empty text
            boxes.append((left, top, left + width, top + height, text))

    merged_boxes = []

    while boxes:
        box = boxes.pop(0)
        left1, top1, right1, bottom1, text1 = box
        merged_text = text1

        to_remove = []

        for other_box in boxes:
            left2, top2, right2, bottom2, text2 = other_box

            # Check if the boxes are close horizontally
            horizontal_close = (abs(top1 - top2) <= VERTICAL_THRESHOLD) and \
                               (left1 <= right2 + HORIZONTAL_THRESHOLD) and \
                               (right1 >= left2 - HORIZONTAL_THRESHOLD)

            # Check if the boxes are close vertically
            vertical_close = (abs(left1 - left2) <= HORIZONTAL_THRESHOLD) and \
                             (top1 <= bottom2 + VERTICAL_THRESHOLD) and \
                             (bottom1 >= top2 - VERTICAL_THRESHOLD)

            if horizontal_close or vertical_close:
                # Merge text boxes
                left1 = min(left1, left2)
                top1 = min(top1, top2)
                right1 = max(right1, right2)
                bottom1 = max(bottom1, bottom2)
                merged_text += ' ' + text2
                to_remove.append(other_box)

        for r in to_remove:
            boxes.remove(r)

        merged_boxes.append((left1, top1, right1, bottom1, merged_text))

    return merged_boxes

def check_mouse_on_text(boxes, x, y):
    # Check if the mouse is over any of the merged text boxes
    for (left, top, right, bottom, text) in boxes:
        if left <= x <= right and top <= y <= bottom and text.strip():
            return text
    return None

def is_foreground_window_changed(initial_window):
    # Check if the currently active window is different from the initial window
    current_window = win32gui.GetForegroundWindow()
    return current_window != initial_window

def delay_scan():
    global timer_active, abc  # Declare abc as global within the function
    if timer_active:
        return
    timer_active = True
    time.sleep(0.1)
    timer_active = False
    if scanning_active:
        print("Re-scanning after delay.")
        image = capture_screen()
        image = preprocess_image(image)
        data = perform_ocr_with_positions(image)
        global boxes
        boxes = merge_text_boxes(data)
        abc = False  # Reset abc after rescan
def main():
    global scanning_active, last_text, boxes, paused, reading_text, abc

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    initial_window = win32gui.GetForegroundWindow()

    print("Press Alt + R to start/stop scanning the screen.")
    print("Scroll or click to update text.")
    print("Press Shift to pause/resume speech.")

    while True:
        if keyboard.is_pressed('alt') and keyboard.is_pressed('r'):
            scanning_active = not scanning_active
            if scanning_active:
                print("Screen scan initiated.")
                image = capture_screen()
                data = perform_ocr_with_positions(image)
                boxes = merge_text_boxes(data)
                initial_window = win32gui.GetForegroundWindow()  # Reset the initial window to the current one
                last_text = ""  # Reset last read text to avoid reading old text
                paused = False  # Reset pause state
                reading_text = False  # Reset reading_text flag
                abc = True
                time.sleep(1)  # Prevent multiple triggers from a single keypress
            else:
                print("Screen scan stopped.")
                boxes = None  # Stop scanning if deactivated
                abc = False
            time.sleep(1)  # Prevent multiple triggers from a single keypress

        if keyboard.is_pressed('shift'):
            paused = not paused
            if paused:
                print("Speech paused.")
                if reading_text:
                    engine.stop()  # Stop reading if currently reading
                    reading_text = False
            else:
                print("Speech resumed.")
            time.sleep(1)  # Prevent multiple triggers from a single keypress

        if scanning_active and boxes and not paused:
            # Get the current mouse position
            x, y = get_mouse_position()

            # Check if the mouse is over any detected text
            text = check_mouse_on_text(boxes, x, y)

            if text and text != last_text:
                # Read the text out loud
                engine.say(text)
                engine.runAndWait()
                last_text = text
                reading_text = True  # Set reading_text flag to True

            # Check if the foreground window has changed
            if is_foreground_window_changed(initial_window):
                print("Window focus changed, stopping scan.")
                scanning_active = False  # Stop scanning if the window focus changes
                boxes = None

        # Check for scroll or click and perform scan
        if win32api.GetAsyncKeyState(win32con.VK_NEXT) & 0x8000 or win32api.GetAsyncKeyState(
                win32con.VK_LBUTTON) & 0x8000 or win32api.GetAsyncKeyState(win32con.VK_PRIOR) & 0x8000:
            print("Scroll or click detected. Stopping and re-scanning.")
            scanning_active = False  # Stop scanning
            boxes = None  # Stop scanning if deactivated
            time.sleep(0.1)  # Wait for 0.1 seconds to see if there are additional scrolls or clicks
            if not timer_active:
                scanning_active = not scanning_active
                if scanning_active:
                    if abc == True:
                        print("Screen scan initiated.")
                        image = capture_screen()
                        data = perform_ocr_with_positions(image)
                        boxes = merge_text_boxes(data)
                        initial_window = win32gui.GetForegroundWindow()  # Reset the initial window to the current one
                        last_text = ""  # Reset last read text to avoid reading old text
                        paused = False  # Reset pause state
                        reading_text = False  # Reset reading_text flag
                        time.sleep(1)  # Prevent multiple triggers from a single keypress



        time.sleep(0.01)  # Small delay to prevent excessive CPU usage


if __name__ == "__main__":
    main()
