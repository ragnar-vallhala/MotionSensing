import cv2
import numpy as np
import matplotlib.pyplot as plt

def calculate_msd(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    msds = []

    previous_frame = None

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if previous_frame is not None:
            # Calculate Optical Flow
            flow = cv2.calcOpticalFlowFarneback(previous_frame, gray_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)

            # Apply 2D Fourier Transform
            f_transform = np.fft.fft2(magnitude)

            # Calculate Motion Spectral Density (MSD)
            msd = np.abs(f_transform)**2
            msds.append(msd)

        previous_frame = gray_frame

    # Average MSD over frames
    average_msd = np.mean(msds, axis=0)
    
    return average_msd, fps

# Assuming 'magnify_motion' is your function to magnify motion in a video
# magnified_video_path = magnify_motion('raw_video.mp4')

raw_msd, fps = calculate_msd('C:\Users\Asus\Downloads\MotionSensing\MotionSensing\videos\baby_motion_evm_2023-09-19-12-03-07.mp4')
magnified_msd, _ = calculate_msd('C:\Users\Asus\Downloads\MotionSensing\MotionSensing\videos\baby_motion_evm_2023-09-19-12-03-07.mp4')

# Define frequency range (0 to 5 Hz)
freq_range = (0, 5)

# Get corresponding indices for the frequency range
freq_indices = np.where((np.fft.fftfreq(raw_msd.shape[0], d=1/fps) >= freq_range[0]) & 
                        (np.fft.fftfreq(raw_msd.shape[0], d=1/fps) <= freq_range[1]))[0]

# Extract relevant frequencies and MSD values
raw_msd_values = raw_msd[freq_indices]
magnified_msd_values = magnified_msd[freq_indices]

# Define the corresponding frequencies for the range
frequencies = np.fft.fftfreq(raw_msd.shape[0], d=1/fps)[freq_indices]

# Plot the normalized MSD values against frequencies
plt.plot(frequencies, raw_msd_values, label='Raw Video')
plt.plot(frequencies, magnified_msd_values, label='Magnified Video')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Normalized Motion Spectral Density')
plt.title('Motion vs Frequency')
plt.legend()
plt.grid(True)
plt.show()
