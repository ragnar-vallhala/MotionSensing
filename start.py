import tkinter as tk
from tkinter import ttk
import vlc
from tkinter import filedialog
import os
from euler_mag import task, exit_event,get_video_mag_prog, set_params
import threading
import sys
from vi import get_opt_flow_prog
import time
import queue

"""
global variables 
"""

threads=[   ]
process_running = False

result = queue.Queue()
initial_high_f_value=0
initial_amplification_value=""
o_level=0
initial_low_f_value=0
initial_step_value=1

"""
global variables end
"""



def play_video():
    global player
    if player is not None:
        player.stop()
        player.release()

    media = instance.media_new(file_path)
    player = instance.media_player_new()
    player.set_media(media)

    player.set_hwnd(video_frame.winfo_id())
    player.play()

def play_pause_video():
    if player is not None:
        if player.get_state() == vlc.State.Paused:
            player.play()
        elif player.get_state() == vlc.State.Playing:
            player.pause()

def open_file():

    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    if file_path:
        play_video()

def apply_options():
    pass

def redirect_stdout():
    class StdoutRedirector:
        def write(self, text):
            if tk.END=="\r":
                output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, text)

    sys.stdout = StdoutRedirector()


def process(): 
    global file_path, process_running,result

    if os.path.exists(file_path):
        
        
        exit_event.set()
        time.sleep(2)
        exit_event.clear()
        progress_bar.stop()
        progress_bar.start()
        print(set_params(levels_var.get(),low_f_var.get(),high_f_var.get(),amplification_var.get(),step_var.get(),file_path))


        thread = threading.Thread(target=task, args=[file_path,result])
        thread.start()
        threads.append(thread)
    else:
        print("Cant find file")

def make_uneditable(widget):
    widget.bind("<KeyPress>", lambda e: "break")


root = tk.Tk()
root.title("Video Player")
root.geometry("1000x600")



levels_var = tk.IntVar(value=o_level)  # Assuming o_level is the initial value
low_f_var = tk.DoubleVar(value=initial_low_f_value)
high_f_var = tk.DoubleVar(value=initial_high_f_value)
amplification_var = tk.DoubleVar(value=initial_amplification_value)
step_var = tk.DoubleVar(value=initial_step_value)



instance = vlc.Instance("--no-xlib")
player = None
file_path = ""

video_frame = tk.Frame(root)
video_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
root.grid_rowconfigure(0, weight=5)
root.grid_columnconfigure(0, weight=5)

# Create a label in the video_frame to indicate video playback (optional)
video_label = ttk.Label(video_frame, text="Video Playback Area", font=("Helvetica", 16))
video_label.pack(pady=10)

paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.grid(row=0, column=1, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

right_frame = ttk.Frame(paned_window, width=200, relief=tk.SUNKEN)
right_frame.pack(fill=tk.BOTH, expand=True)

open_button = ttk.Button(right_frame, text="Open Video", command=open_file)
open_button.pack(pady=10)

play_pause_button = ttk.Button(right_frame, text="Play/Pause Video", command=play_pause_video)
play_pause_button.pack(pady=10)

options_label = ttk.Button(right_frame, text="Process", command=process )
options_label.pack(pady=10)

label = tk.Label(right_frame,text="Levels")
label.pack(pady=10)
levels_spinbox = tk.Spinbox(right_frame, from_=1, to=10, textvariable=levels_var)
levels_spinbox.pack(padx=20, anchor="n")

label = tk.Label(right_frame,text="Lower Frequency")
label.pack(pady=10)
low_f_spinbox = tk.Spinbox(right_frame, from_=0.0, to=100.0, textvariable=low_f_var)
low_f_spinbox.pack(padx=20, anchor="n")

label = tk.Label(right_frame,text="High Frequency")
label.pack(pady=10)
high_f_spinbox = tk.Spinbox(right_frame, from_=0.0, to=100.0, textvariable=high_f_var)
high_f_spinbox.pack( padx=20, anchor="n")

label = tk.Label(right_frame,text="Amplification")
label.pack(pady=10)
amplification_spinbox = tk.Spinbox(right_frame, from_=0.0, to=10.0, textvariable=amplification_var)
amplification_spinbox.pack(padx=20, anchor="n")

label = tk.Label(right_frame,text="Step Difference")
label.pack(pady=10)
step_spinbox = tk.Spinbox(right_frame, from_=0.0, to=10.0, textvariable=step_var)
step_spinbox.pack(padx=20, anchor="n")


progress_bar = ttk.Progressbar(right_frame, mode="determinate", length=100)
progress_bar.pack( anchor="center", pady=40)
if process_running:
    progress_bar['value'] = get_video_mag_prog()


if result._qsize():
    if result.get():
        progress_bar.stop()

# Add your options widgets here

apply_options_button = ttk.Button(right_frame, state="disabled", text="Apply Options", command=apply_options)
apply_options_button.pack(pady=10)

output_text = tk.Text(right_frame, wrap="word", height=10, width=40)
output_text.pack(padx=10, pady=10, expand=True, fill="both")
make_uneditable(output_text)
redirect_stdout()

sizegrip = ttk.Sizegrip(right_frame)
sizegrip.pack(side=tk.BOTTOM, anchor=tk.SE)


root.mainloop()
exit_event.set()

for thread in threads:
    thread.join()
print("closed")
sys.exit()