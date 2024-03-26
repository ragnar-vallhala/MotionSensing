import cv2
import numpy as np

cap = cv2.VideoCapture(0)
while True:
    ret,frame = cap.read()
# Load the input video frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Number of decomposition levels (adjust as needed)
    num_levels = 4

    # Initialize an empty list to store the decomposed image pyramid
    pyramid = []

    # Perform spatial decomposition (Gaussian pyramid)
    current_frame = frame.copy()
    for _ in range(num_levels):
        pyramid.append(current_frame)
        current_frame = cv2.pyrDown(current_frame)

    # Select a specific level to amplify motion (e.g., the second level)
    level_to_amplify = 1  # Adjust as needed

    # Amplify motion in the selected level (e.g., increase contrast)
    amplified_frame = pyramid[level_to_amplify] * 2  # Amplify the intensity

    # Reconstruct the amplified frame
    for i in range(level_to_amplify):
        amplified_frame = cv2.pyrUp(amplified_frame)

    # Display the original frame and the amplified frame
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Amplified Frame', amplified_frame)

    # Wait for a key press and then close the windows
    cv2.waitKey(1)
cv2.destroyAllWindows()
