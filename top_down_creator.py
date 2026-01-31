import cv2
import numpy as np

# List to store our 4 points
points = []

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        # Draw a circle where you clicked
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Original CCTV', img)
        
        if len(points) == 4:
            transform_image()

def transform_image():
    # 1. Prepare the source points from your clicks
    pts1 = np.float32(points)
    
    # 2. Define the destination (the "Perfect Rectangle")
    # We'll make it 500x800, but you can change this ratio
    width, height = 500, 800
    pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    
    # 3. Calculate the Matrix and Warp
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(original_img, matrix, (width, height))
    
    cv2.imshow('Top Down View', result)
    print("Transformation Complete!")

# Load your image here
img = cv2.imread('camera_view.png')
original_img = img.copy()

cv2.imshow('Original CCTV', img)
cv2.setMouseCallback('Original CCTV', click_event)

print("Click the 4 corners of a rectangular area in order: Top-Left, Top-Right, Bottom-Right, Bottom-Left.")
cv2.waitKey(0)
cv2.destroyAllWindows()