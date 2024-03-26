import cv2
import numpy as np
from create_collapse_pyramids import *
from filters import *
from amplification import *
import argparse
import vi
import threading
exit_event = threading.Event()
import os
import multiprocessing  as mps
"""
global variables 
"""
video_mag_prog = 0


"""
global variables end
"""




#### Config params ####
levels = 6
low_f =0.5
high_f = 1.5
amplification = [0,50,50,50,50,0]
nq_freq = 0
step_diff = 1
#amplification = [0,50,50,0]
#amplification = [50,50]
chrome_attenuation = 5
########################
def set_params(i_levels, i_low_f, i_high_f, i_amplification,i_step_diff,file_path):
    set_nq(file_path)
    global levels, low_f, high_f,amplification, nq_freq, step_diff
    # if (str(i_levels).isnumeric() and str(i_low_f).isnumeric() and str(i_high_f).isnumeric() and i_low_f>0 and i_low_f<nq_freq  and i_high_f<nq_freq and i_high_f>0 and i_high_f>i_low_f and i_amplification>0): 
    if i_low_f>=i_high_f:
        return "Highest Frequency should be greater than lowest frequency"
    if step_diff<=0:
        return "Step difference should be greater than 0"
    

    levels = int(i_levels)
    low_f = i_low_f
    high_f = i_high_f
    amplification = [0]
    if levels>2:
        for i in range(int(levels)-2):
            amplification.append(int(i_amplification))
    if levels>=3:
        amplification.append(0)

    step_diff = i_step_diff
    print(i_levels, i_low_f, i_high_f, i_amplification)
    return "Values updated"
    
    # return False

def set_nq(video_file):
    cap = cv2.VideoCapture(video_file)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    global nq_freq
    nq_freq=fps/2
    cap.release()
    print(nq_freq)


def perFreq(levels,low_f,high_f,amplification,video_file):
    if not exit_event.is_set():
        fre = (low_f+high_f)/2
        
        output_filename = video_file.split('.')[0]+"frq" +str(fre) + 'amp.mp4'
        

        print("Output file",output_filename)
        cap = cv2.VideoCapture(video_file)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        global nq_freq
        nq_freq=fps/2
        print(f'fps of video: {fps}')


        frame_cntr = 0

        pyd_dict = {i:[] for i in range(levels)}
        filt_pyd_dict = {i:[] for i in range(levels)}

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            #print(frame.shape)
            frame = cv2.resize(frame, (1024, 512))
            lp_pyd = create_laplacian_pyd(frame, levels)

            for i in range(levels):
                pyd_dict[i].append(lp_pyd[i])

            frame_cntr+=1

        for i in range(levels):
            video_mag_prog = i*100/levels
            if exit_event.is_set():
                return
            print(f'processing level: {i}')
            pyd_dict[i] = np.array(pyd_dict[i])
            if amplification[i] > 0:
                #filt_pyd_dict[i] = ideal_temporal_filter(pyd_dict[i], fps, low_f, high_f)
                filt_pyd_dict[i] = butter_bandpass_filter(pyd_dict[i], low_f, high_f, fps, order=2)
                filt_pyd_dict[i] *= amplification[i]
                #filt_pyd_dict[i] = color_amplification(filt_pyd_dict[i], amplification[i], chrome_attenuation)
                filt_pyd_dict[i] = pyd_dict[i] + filt_pyd_dict[i]
            else:
                filt_pyd_dict[i] = pyd_dict[i]

        filt_frame_list = []

        for i in range(pyd_dict[0].shape[0]):
            pyd = []
            for j in range(levels):
                pyd.append(filt_pyd_dict[j][i])
            filt_img = collapse_laplacian_pyd(pyd, levels)
            filt_frame_list.append(filt_img)

        cap.release()
        print(f'number of frames processed: {frame_cntr}')
        print('saving video',output_filename)

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        h,w = filt_frame_list[0].shape[:2]
        writer = cv2.VideoWriter(output_filename, fourcc, fps, (w,h), 1)
        for i in range(len(filt_frame_list)):
            if exit_event.is_set():
                return
            writer.write(cv2.convertScaleAbs(filt_frame_list[i]))
        writer.release()
        if exit_event.is_set():
            return
        print("*******Frequency and optical flow in X and Y direction",vi.fn(output_filename),"*******")



import queue
def task(video_file,queue):
    if not exit_event.is_set():
        tasks = []
        global levels, low_f, high_f,amplification, nq_freq, step_diff
        working_f = low_f+step_diff
        while working_f<high_f:
            print("Operating Frequency",(working_f+low_f)/2)
            perFreq(levels,low_f,high_f,amplification,video_file)
            task = mps.Process(target=perFreq,args=[levels,low_f,high_f,amplification,video_file])
            tasks.append(task)
            task.start()
            task.join()   
            # Increment low_f and high_f
            low_f += step_diff
            working_f += step_diff
            
        
        for task in tasks:
            task.join()   
            pass
    queue.put(True)
    
def get_video_mag_prog():
    return video_mag_prog