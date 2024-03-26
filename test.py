import cv2
import numpy as np
from scipy.signal import butter, filtfilt
import python_eulerian_video_magnification


def temporal_filter(frame, low_cutoff, high_cutoff, fps):
    nyquist = 0.5 * fps
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist
    b, a = butter(2, [low, high], btype='band')

    # Apply filter to each color channel separately
    filtered_channels = [filtfilt(b, a, frame[:,:])]
    filtered_frame = np.stack(filtered_channels, axis=2)

    return filtered_frame


def spatial_smoothing(frame, sigma):
    smoothed_frame = cv2.GaussianBlur(frame, (0, 0), sigma)
    return smoothed_frame

def build_gaussian_pyramid(frame, levels):
    pyramid = [frame]
    for _ in range(levels - 1):
        frame = cv2.pyrDown(frame)
        pyramid.append(frame)
    return pyramid

def reconstruct_frame(pyramid):
    for i in range(len(pyramid) - 1, 0, -1):
        expanded = cv2.pyrUp(pyramid[i])
        pyramid[i - 1] += expanded
    return pyramid[0]

def amplify_motion(input_video_path, output_video_path, alpha=50, low_cutoff=0.4, high_cutoff=3, pyramid_levels=6, sigma=2):
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    prev_frame = None
    z=0
    ret = True
    while ret:
        z+=1
        print(z)
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        # Step 1: Preprocessing
        filtered_frame = temporal_filter(frame, low_cutoff, high_cutoff, fps)
        smoothed_frame = spatial_smoothing(filtered_frame, sigma)

        # Step 2: Gaussian Pyramid Construction
        pyramid = build_gaussian_pyramid(smoothed_frame, pyramid_levels)

        # Step 3: Motion Estimation
        if prev_frame is not None:
            motion = cv2.absdiff(pyramid[0], prev_frame)
            motion_pyramid = build_gaussian_pyramid(motion, pyramid_levels)

            # Step 4: Motion Magnification
            for i in range(pyramid_levels):
                motion_pyramid[i] *= alpha

            # Step 5: Reconstruction
            amplified_frame = reconstruct_frame(motion_pyramid)
            amplified_frame = np.clip(amplified_frame, 0, 255).astype(np.uint8)

            out.write(amplified_frame)

        prev_frame = pyramid[0]

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    input_video_path = "sub1.mp4"
    output_video_path = "output_video1.avi"
    amplify_motion(input_video_path, output_video_path)
