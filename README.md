# AadhaarVision  
**OCR-based Aadhaar Card Detector & Data Extractor** using **OpenCV** and **EasyOCR**  

---

## 📌 Overview
AadhaarVision is a Python project that scans Aadhaar cards from a live camera feed or static image, detects the document, applies perspective correction, and extracts important details such as:
- **Name**
- **Date of Birth (DOB) & Age**
- **Gender**
- **Aadhaar Number**

This is achieved using:
- **OpenCV** for image processing and document detection  
- **EasyOCR** for text recognition  
- **Regex** for pattern-based information extraction  

---

## 🖼 Features
- 📷 Live Aadhaar scanning via webcam or IP camera feed  
- 📝 Text extraction using **EasyOCR**  
- 🔍 Automatic detection of Name, DOB, Gender, Aadhaar Number  
- 🔄 Perspective transformation for tilted scans  
- ⚡ Adjustable Canny edge detection thresholds using trackbars  
- 💾 Saves scanned Aadhaar images inside a `Scanned/` folder  

---

## 📂 Project Structure
AadhaarVision/
-│-- main.py # Main script (runs the scanner)
-│-- utils.py # Utility functions (image stacking, contour detection, etc.)
-│-- Scanned/ # Saved Aadhaar scan images
-│-- README.md # Documentation

---

##📄 Example OCR Output
-✅ Saved: Scanned/myImage0.jpg
-Name: Chiranjeeb Mishra
-DOB: 14/08/2003
-Age: 22
-Gender: Male-
-Aadhaar Number: 5784 6789 2567

---

##How It Works
1. Captures a live feed from the webcam or IP camera.
2. Detects the largest rectangular contour (document).
3. Applies a perspective warp for a flat scan-like image.
4. Passes the processed image to EasyOCR for text extraction.
5. Uses regex to identify Name, DOB, Gender, and Aadhaar Number.
6. Saves both the processed image and extracted details

---

##Important
- Install these before run the python file:
    opencv-python
    numpy
    easyocr

- Create The project structure menton above
- If want to scan from phone then download the Ip Webcam.
    link: https://play.google.com/store/apps/details?id=com.pas.webcam
- If want scan from image then webCamFeed = False.
- After that you can run the main.py.
- When the img show press 's' for scan and saved.
- After saved it will show the details in the terminal.
