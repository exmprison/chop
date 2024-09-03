# Chop Setup

## Introduction

**Chop** is a program that helps people who are blind and low-vision by providing AI image descriptions, OCR-powered screen reading, and OCR-powered image accessibility.

### AI Image Describing

Using AI, we can get a description of an image.

### OCR-Powered Screen Reader

Using OCR, this screen reader can read any program or website, even if they are not accessible to normal screen readers. It takes the location of the text from the OCR scan and lets you hover your cursor over the text to read aloud.

> **Note:** This uses OCR and is not always accurate. It is recommended to use when a program is not working with a normal screen reader.

### OCR-Powered Image Accessibility

This feature uses OCR to get the locations of text on an image. It will place the readable text over the non-accesible text on an image. Therefore, images can be read with a screen reader, and the text can keep its location for images like maps, where you need to know where things are.

## Installation

### Step 1: Install Python

Make sure you have Python installed. You can get it at: [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Step 2: Install Tesseract

Make sure you have Tesseract installed. You can get the installer file at: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

### Step 3: Get an Azure Account

You will need an Azure account. You can make one at [https://azure.microsoft.com/free/cognitive-services/](https://azure.microsoft.com/free/cognitive-services/)

After signing up, get an Azure API key at: [https://portal.azure.com/#create/Microsoft.CognitiveServicesComputerVision](https://portal.azure.com/#create/Microsoft.CognitiveServicesComputerVision)

### Step 4: Download the Python Files

Download the Python files from the GitHub repository.

To download the GitHub files to your computer, go to the big green button that says **Code** near the top of the webpage. When you click it, at the bottom of the popup it will say, **Download ZIP**. Click that button.

### Step 5: Extract the Files

Extract the files to your preferred location.

### Step 6: Open Files in a Code Editor (Optional)

If you have a code editor, open these files as a new project.

If not, move the files anywhere you want on your computer. It is recommended to place them in a new folder. For example, mine are in `"C:\Users\Henry\chop"`. Remember that "Henry" is my name, and your name would be in place of that if you want to place your files where I did.

### Step 7: Open Terminal in the Folder

Click **Shift** and **Right Click** while hovering over your folder and click **Open in Terminal**.

### Step 8: Install Dependencies

Run these commands one at a time in the terminal:

pip install pytesseract

pip install Pillow

pip install pyttsx3

pip install keyboard

pip install pywin32

pip install pyperclip

pip install azure-ai-vision-imageanalysis

### Step 9: Configure the API Key
Go back to your files, and right-click on your main.py file. Click Open with and select Notepad.

Under the first few lines, you should see something saying endpoint = '' and key = ''. Follow the instructions in the code to set these values. Do not share that key with anyone.

### Step 10: Run the Program
To run the main.py file, which handles AI image describing and AI image accessibility, use the command:

python mainv1.py

That command only runs the AI image describing and AI image accessibility. 

To run the ocr-sr.py file, run "python ocr-crv1.py".

python ocr-crv1.py

# How To Use

## main.py

You can use main.py which gives image descriptions and makes images accessible by first running the file. As described above, you will use python mainv1.py to run it. Now, right click on any image. It does not work with images on google search, but you can just click on an image from google and go to the website. After right clicking, click copy image address. The program will detect that you have copied an image address and give you a description. If you do not see a window pop up, then click alt and tab on your keyboard, and look for it as the last tab. After clicking “okay” on the image description, it will ask if you want to make the image accessible. If you click “yes”, it will make the image accessible, and if you click “no”, it will not. 

## ocr-sr.py 

This python is for the ocr powered screen reader. When run with python ocr-srv1.py, nothing will happen at first besides some directions that will be printed into the terminal. When you are at your program that does not work with a normal screen reader, you can click alt and r to start up the screen reader. Move your mouse around and it will read the text. You can left click to have the ocr reset for when your screen changes, and you can click alt r to stop the program. 


### If you have any ideas for the program, or need help, go to the Discussion tab. From there, comment on my Discussion, or make a new discussion. 

### If you have any bugs, go to the issues tab, and make a new issue. 
