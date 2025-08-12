import cv2
import numpy as np

# =========================
# Utility Functions
# =========================

def stackImages(imgArray, scale, labels=[]):
    """
    Stacks multiple images into a single display window.
    Can handle both grayscale and colored images.
    Optionally draws labels on each image.
    """
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]

    if rowsAvailable:
        # Resize all images in the grid and convert grayscale to color
        for x in range(rows):
            for y in range(cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)

        # Create blank image placeholder
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows

        # Horizontally stack each row
        for x in range(rows):
            hor[x] = np.hstack(imgArray[x])

        # Vertically stack all rows
        ver = np.vstack(hor)
    else:
        # If single row of images
        for x in range(rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        ver = np.hstack(imgArray)

    # Add labels if provided
    if len(labels) != 0:
        eachImgWidth = int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        for d in range(rows):
            for c in range(cols):
                cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
                              (c * eachImgWidth + len(labels[d]) * 13 + 27, 30 + eachImgHeight * d),
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(ver, labels[d][c], (eachImgWidth * c + 10, eachImgHeight * d + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)
    return ver


def reorder(myPoints):
    """
    Reorders the four points of a contour to match:
    top-left, top-right, bottom-left, bottom-right.
    This helps in perspective transformation.
    """
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]  # Top-left
    myPointsNew[3] = myPoints[np.argmax(add)]  # Bottom-right

    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]  # Top-right
    myPointsNew[2] = myPoints[np.argmax(diff)]  # Bottom-left
    return myPointsNew


def biggestContour(contours):
    """
    Finds the largest contour that has exactly four corners.
    This is usually the document we want to scan.
    """
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:  # Ignore very small contours
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area


def drawRectangle(img, biggest, thickness):
    """
    Draws a rectangle (using four lines) around the detected document contour.
    """
    cv2.line(img, tuple(biggest[0][0]), tuple(biggest[1][0]), (0, 255, 0), thickness)
    cv2.line(img, tuple(biggest[0][0]), tuple(biggest[2][0]), (0, 255, 0), thickness)
    cv2.line(img, tuple(biggest[3][0]), tuple(biggest[2][0]), (0, 255, 0), thickness)
    cv2.line(img, tuple(biggest[3][0]), tuple(biggest[1][0]), (0, 255, 0), thickness)
    return img


def nothing(x):
    """Placeholder function for trackbars."""
    pass


def initializeTrackbars():
    """Creates trackbars for adjusting Canny edge detection thresholds."""
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 65, 255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 95, 255, nothing)


def valTrackbars():
    """Returns the current positions of the threshold trackbars."""
    Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    return Threshold1, Threshold2

