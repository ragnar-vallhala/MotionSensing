import cv2 as cv

"""
global variables 
"""

opt_flow_prog = 0



def fn(video_file):
    scale = 4.0
    cap  = cv.VideoCapture(video_file)
    prevFrame,frame,prev_diff ,diff =None,None,None,None


    out=[]


    output_filename = video_file.split('.')[0] + '_opt.mp4'
    fps = int(cap.get(cv.CAP_PROP_FPS))
    nFrame = cap.get(cv.CAP_PROP_FRAME_COUNT)
    print("Frames:",nFrame)
    frm_cnt=0
    sumx,sumy=0, 0
    while cap.isOpened():
        opt_flow_prog = frm_cnt*100/nFrame
        frm_cnt+=1
        prevFrame = frame
        ret,frame = cap.read()
        if ret==False:
            break

        if prevFrame is not None and frame is not None:
        
            gray_prevFrame = cv.cvtColor(prevFrame, cv.COLOR_BGR2GRAY)
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            prev_diff = diff
            
            diff = cv.subtract(gray_frame,gray_prevFrame)
            #diff = cv.Canny(diff,75,255)

            disp  = frame.copy()

            if prev_diff is not None and diff is not None:

            
                flow = cv.calcOpticalFlowFarneback(gray_prevFrame,gray_frame, None, 0.5, 3, 45, 3, 5, 2.0, 0)
                #flow = cv.calcOpticalFlowFarneback(prev_diff,diff, None, 0.5, 3, 45, 3, 5, 0.5, 0)
                
                for y in range(0, frame.shape[0], 10):
                    for x in range(0, frame.shape[1], 10):
                        dx, dy = flow[y, x]
                        sumx+=abs(dx)
                        sumy+=abs(dy)
                        #file.write(str(dx)+","+str(dy)+"\n")
                        if abs(dx)>0.1 and abs(dx)<50 and abs(dy)>0.1 and abs(dy)<50: 
                            col  = (50*int(abs(dx)),50*int(abs(dy)),50*int(abs(dx+dy)))
                            cv.arrowedLine(disp, (x, y), (int(x+dx*scale), int(y+dy*scale)),col , 1)

            cv.imshow("Win",disp)
            out.append(disp)
            delay = 1E3/float(cap.get(cv.CAP_PROP_FPS))
            key = cv.waitKey(1)
            if key==27:
                break

    cap.release()

    cv.destroyAllWindows()
    fourcc = cv.VideoWriter_fourcc('M','J','P','G')
    h,w = out[0].shape[:2]
    writer = cv.VideoWriter(output_filename, fourcc, fps, (w,h), 1)
    for i in range(len(out)):
        writer.write(cv.convertScaleAbs(out[i]))
    writer.release()
    return sumx,sumy

def get_opt_flow_prog():
    return opt_flow_prog