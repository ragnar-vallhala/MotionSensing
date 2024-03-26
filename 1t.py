import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load an example image
image = cv2.imread('2.png', cv2.IMREAD_GRAYSCALE)

# Apply Fourier Transform to the image
f_transform = np.fft.fft2(image)
f_transform_shifted = np.fft.fftshift(f_transform)

# Calculate the magnitude spectrum (logarithmic scale)
magnitude_spectrum = np.log(np.abs(f_transform_shifted) + 1)
nwr = [[i>8 for i in magnitude_spectrum[j]] for j in range(len(magnitude_spectrum))]
# Display the original image and magnitude spectrum
plt.subplot(121), plt.imshow(image, cmap='gray')
plt.title('Original Image'), plt.axis('off')
plt.subplot(122), plt.imshow(nwr, cmap='gray')
plt.title('Magnitude Spectrum'), plt.axis('off')
plt.show()
