import cv2
import numpy as np
import easyocr
import re
import warnings
import utils
from datetime import datetime

warnings.filterwarnings("ignore")

reader = easyocr.Reader(['en'])

# =========================
# Config
# =========================
webCamFeed = True
pathImage = "Aadhaar.jpg"  # Path for testing with a static image
cap = cv2.VideoCapture("https://172.26.0.35:8080/video")  # Webcam / IP camera feed
cap.set(10, 160)  # Set brightness
heightImg = 650
widthImg = 1000
count = 0
detection = False

# Initialize threshold adjustment sliders
utils.initializeTrackbars()

# =========================
# Main Loop
# =========================
while True:
    # Read frame from webcam or static image
    if webCamFeed:
        success, img = cap.read()
    else:
        img = cv2.imread(pathImage)

    # Resize to fixed size
    img = cv2.resize(img, (widthImg, heightImg))

    # Preprocessing: convert to grayscale and blur
    imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

    # Canny edge detection with trackbar-controlled thresholds
    thres = utils.valTrackbars()
    imgThreshold = cv2.Canny(imgBlur, thres[0], thres[1])

    # Dilation and erosion to strengthen edges
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)
    imgThreshold = cv2.erode(imgDial, kernel, iterations=1)

    # Find all contours
    imgContours = img.copy()
    imgBigContour = img.copy()
    contours, _ = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)

    #The Output Window
    if len(imgContours) != 0:
        cv2.imshow("Camera", imgContours)
    else:
        cv2.imshow("Camera", img)
    # Find largest document-like contour
    biggest, maxArea = utils.biggestContour(contours)
    if biggest.size != 0:
        biggest = utils.reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)
        imgBigContour = utils.drawRectangle(imgBigContour, biggest, 2)

        # Perspective transform (warp) to get a top-down view
        pts1 = np.float32(biggest)
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
        detection = True

        # Convert warped image to grayscale and apply adaptive threshold
        imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

        imageArray = ([img, imgGray, imgThreshold, imgContours],
                      [imgBigContour, imgWarpColored, imgWarpGray, imgAdaptiveThre])
    else:
        # No big contour found → show blank placeholders
        imageArray = ([img, imgGray, imgThreshold, imgContours],
                      [imgBlank, imgBlank, imgBlank, imgBlank])

    # Stack images for side-by-side comparison
    labels = [["Original", "Gray", "Threshold", "Contours"],
              ["Biggest Contour", "Warp Perspective", "Warp Gray", "Adaptive Threshold"]]
    stackedImage = utils.stackImages(imageArray, 1, labels)
    # cv2.imshow("Output", stackedImage) #If you want to see the comparison of all window

    # OCR and save when 'S' key is pressed
    if detection:
        if cv2.waitKey(1) & 0xFF == ord('s'):
            save_path = f"Scanned/myImage{count}.jpg"
            cv2.imwrite(save_path, imgWarpColored)
            print(f"✅ Saved: {save_path}")
            
            #Read the text from image usin easyocr
            result = reader.readtext(save_path)

            # Regex patterns for extracting Aadhaar info
            name_pattern = r"([A-Z][a-z]*\.?(?:\s[A-Z][a-z]*\.?)+|[A-Z]{2,}(?:\s[A-Z]{2,})+)"

            #If the text getting this stirng we can fillter it.
            # stop_words = {"Government", "India", "Unique", "Authority", "Card", "Aadhaar"}

            #The pattern for Date-Of-Birth.
            dob_pattern = r"(\d{2}[\/\-]\d{2}[\/\-]\d{4})"

            #The pattern for Gender.
            gender_pattern = r"(Male|Female|Transgender)"

            #The pattern for Aadhaar Number.
            aadhaar_pattern = r"\d{4}\s?\d{4}\s?\d{4}"

            # Store matches
            name_matches, dob_matches, gender_matches, aadhaar_matches = [], [], [], []
            for _, text, _ in result:
                # name_matches.extend(re.findall(name_pattern1, text, re.IGNORECASE))
                name_matches.extend(re.findall(name_pattern, text))                
                dob_matches.extend(re.findall(dob_pattern, text, re.IGNORECASE))
                gender_matches.extend(re.findall(gender_pattern, text, re.IGNORECASE))
                aadhaar_matches.extend(re.findall(aadhaar_pattern, text))

            # Display found info
            found = False
            n = len(name_matches)
            if name_matches:
                for i in range(n):
                    length_without_spaces = len(name_matches[i].replace(" ", ""))
                    if length_without_spaces > 10:
                        print(name_matches[i])
                        found = True
                #To view the all text which match the pattern
                # print("Name:", name_matches)
                
            if dob_matches:
                #This is for age Calculate.
                dob_str = dob_matches[0].strip()
                match = re.search(r"\d{2}/\d{2}/\d{4}", dob_str)
                if match:
                        dob_clean = match.group()
                        dob = datetime.strptime(dob_clean, "%d/%m/%Y").date()
                        today = datetime.today().date()
                        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                        print("DOB:", dob_clean)
                        print("Age:", age)
                        found = True
                else:
                 print("No valid DOB found")                
            if gender_matches:
                print("Gender:", gender_matches[0])
                found = True
            if aadhaar_matches:
                print("Aadhaar Number:", aadhaar_matches[0])
                found = True
            if not found:
                print("❌ Scan Failed. Please try again with a horizontal scan.")

            count += 1
            cv2.waitKey(300)

    # Quit if 'Q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
