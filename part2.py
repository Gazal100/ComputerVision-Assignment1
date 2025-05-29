import cv2
import numpy as np
import matplotlib.pyplot as plt

img1 = cv2.imread('image.png')
img2 = cv2.imread('opencv_logo.png')

if img1 is None or img2 is None:
    print("Error: One or both images not found.")
    exit()

if img1.shape != img2.shape:
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

alpha = 0.5 

blend = ((1 - alpha) * img1 + alpha * img2)

cv2.imwrite('manual_blend.jpg', blend)
cv2.imshow('Manual Blend', blend)
cv2.waitKey(0)
cv2.destroyAllWindows()
