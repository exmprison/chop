import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import time
import re
import threading
import pyperclip
import webbrowser
import ctypes

# Set the values of your computer vision endpoint and computer vision key
try:
    # endpoint = os.environ["VISION_ENDPOINT"]
    endpoint = 'your endpoint here'
    #put your endpoint between the ''. It should look like this 'your line here' 
    # key = os.environ["VISION_KEY"]
    key = 'your key here'
    #Place your key there. It should look like 'your key'
    #important, do not shere your key with anyone. If you want to shair this python, send someone the file strate from the github
    if not endpoint or not key:
        raise KeyError
except KeyError:
    print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
    print("Set them before running this sample.")
    exit()

# Initialize the Azure Image Analysis client
client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Regex pattern to match image URLs
image_url_pattern = re.compile(r"https?:\/\/.*\.(?:png|jpg|jpeg|gif|bmp|tiff)", re.IGNORECASE)


def analyze_image(image_url):
    try:
        # Analyze the image using Azure Cognitive Services
        result = client.analyze_from_url(
            image_url=image_url,
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
            gender_neutral_caption=True
        )

        # Display caption results in a pop-up
        caption_text = "No caption available."
        if result.caption is not None:
            caption_text = f"'{result.caption.text}', Confidence: {result.caption.confidence:.4f}"

        ctypes.windll.user32.MessageBoxW(
            None,
            f"Image Caption:\n{caption_text}",
            "Image Description",
            0
        )

        # Print OCR (Read) results in the terminal
        print("\nRead:")
        ocr_data = []
        if result.read is not None and result.read.blocks:
            for block in result.read.blocks:
                for line in block.lines:
                    line_info = {
                        'text': line.text,
                        'bounding_box': line.bounding_polygon
                    }
                    words = []
                    for word in line.words:
                        words.append({
                            'text': word.text,
                            'bounding_box': word.bounding_polygon,
                            'confidence': word.confidence
                        })
                    line_info['words'] = words
                    ocr_data.append(line_info)
                    # Print line and word details
                    print(f"  Line: '{line.text}', Bounding box: {line.bounding_polygon}")
                    for word in line.words:
                        print(
                            f"    Word: '{word.text}', Bounding polygon: {word.bounding_polygon}, Confidence: {word.confidence:.4f}")
        else:
            print("  No text detected.")

        return result.caption, ocr_data

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None, None


def create_webpage(image_url, ocr_data):
    try:
        # Download the image to a temporary file
        import requests
        from PIL import Image
        from io import BytesIO

        response = requests.get(image_url)
        if response.status_code != 200:
            print("Failed to download the image.")
            return

        image = Image.open(BytesIO(response.content))
        image_width, image_height = image.size

        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Image with OCR Text</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    position: relative;
                    width: {image_width}px;
                    height: {image_height}px;
                    background-image: url('{image_url}');
                    background-size: cover;
                }}
                .text {{
                    position: absolute;
                    background-color: rgba(255, 255, 255, 0.5);
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-size: 14px;
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body>
            <div class="container">
        """

        # Add text elements based on OCR data
        for line in ocr_data:
            # Calculate the position based on bounding box
            bbox = line['bounding_box']
            # Assuming bounding_box is a list of points [{'x': , 'y': }, ...]
            x_coords = [point['x'] for point in bbox]
            y_coords = [point['y'] for point in bbox]
            x = min(x_coords)
            y = min(y_coords)
            width = max(x_coords) - x
            height = max(y_coords) - y

            # Add each word as a separate text element
            for word in line['words']:
                word_bbox = word['bounding_box']
                word_x = min(point['x'] for point in word_bbox)
                word_y = min(point['y'] for point in word_bbox)
                word_width = max(point['x'] for point in word_bbox) - word_x
                word_height = max(point['y'] for point in word_bbox) - word_y

                # Add the word to the HTML
                html_content += f"""
                    <div class="text" style="left: {word_x}px; top: {word_y}px; width: {word_width}px; height: {word_height}px;">
                        {word['text']}
                    </div>
                """

        # Close the container and body
        html_content += """
            </div>
        </body>
        </html>
        """

        # Save the HTML to a temporary file
        html_file = "image_with_text.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\nWebpage '{html_file}' created successfully.")
        # Open the webpage in the default browser
        webbrowser.open(f'file://{os.path.realpath(html_file)}')

    except Exception as e:
        print(f"Error creating webpage: {e}")


def prompt_user_and_create_webpage(caption, ocr_data):
    # Create a pop-up with Yes/No buttons
    user_input = ctypes.windll.user32.MessageBoxW(
        None,
        "Would you like to make this image accessible?",
        "Accessibility Prompt",
        4  # Yes/No buttons
    )

    if user_input == 6:  # 6 is the response code for 'Yes'
        print("Creating webpage with image and OCR text...")
        create_webpage(image_url, ocr_data)
    else:
        print("No action taken.")


def monitor_clipboard():
    last_clipboard = ""
    while True:
        time.sleep(1)  # Check clipboard every second
        try:
            current_clipboard = pyperclip.paste()
        except pyperclip.PyperclipException:
            # If clipboard access fails, skip this iteration
            continue

        # Only proceed if clipboard content has changed
        if current_clipboard != last_clipboard:
            last_clipboard = current_clipboard
            # Check if the clipboard content is an image URL
            if image_url_pattern.match(current_clipboard):
                print(f"\nDetected image URL: {current_clipboard}")
                global image_url
                image_url = current_clipboard
                caption, ocr_data = analyze_image(image_url)
                if caption or ocr_data:
                    prompt_user_and_create_webpage(caption, ocr_data)
            else:
                print("\nNo valid image URL detected in clipboard.")


if __name__ == "__main__":
    print("Starting clipboard monitoring...")
    # Start clipboard monitoring in the main thread
    monitor_clipboard()
