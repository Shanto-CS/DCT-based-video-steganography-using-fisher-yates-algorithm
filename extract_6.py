from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from scipy.fftpack import dct, idct
import os
import random

# Fisher-Yates shuffle function for extraction
def fisher_yates_shuffle(data, seed):
    random.seed(seed)
    for i in range(len(data) - 1, 0, -1):
        j = random.randint(0, i)
        data[i], data[j] = data[j], data[i]
    return data

# Extraction function
def extract_data_from_video(video_path, output_image_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    shuffle_indices = fisher_yates_shuffle(list(range(frame_count)), 42)
    extracted_data = np.zeros((512, 512, 3), dtype=np.uint8)

    frame_index = 0
    success = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index == shuffle_indices[0]:  # Extract from the first frame used for embedding
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            y_channel = yuv_frame[:, :, 0]

            dct_frame = cv2.dct(np.float32(y_channel) / 255.0)
            for i in range(512):
                for j in range(512):
                    value = dct_frame[i % 64, j % 64] * 255.0
                    extracted_data[i, j, 0] = np.clip(value, 0, 255)  # Extract R channel

            success = True
            break

        frame_index += 1

    cap.release()
    if success:
        extracted_image = Image.fromarray(extracted_data, 'RGB')
        extracted_image.save(output_image_path)
        messagebox.showinfo("Success", "Image extracted and saved as " + output_image_path)
    else:
        messagebox.showerror("Error", "Failed to extract image.")

# GUI setup
win = Tk()
win.geometry('800x500')
win.config(bg='#e6dfcc')

open_video_file = None
output_image_path = "extracted_image.png"

# Open video function
def video_open():
    global open_video_file
    open_video_file = filedialog.askopenfilename(filetypes=(('MP4 files', '*.mp4'),))
    if open_video_file:
        cap = cv2.VideoCapture(open_video_file)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame).resize((150, 150), Image.LANCZOS)
            video_thumbnail = ImageTk.PhotoImage(frame)
            video_label.configure(image=video_thumbnail)
            video_label.image = video_thumbnail

# Extract data button action
def on_extract():
    if open_video_file:
        extract_data_from_video(open_video_file, output_image_path)
    else:
        messagebox.showerror("Error", "Please select a video file.")

# GUI components
Label(win, text='Video Steganography - Extraction', font='impact 20 bold', fg='black', bg='#e6dfcc').pack(pady=10)
video_label = Label(win, bg='#a8a7a3')
video_label.place(x=200, y=100)

Button(win, text='Open Video', bg='#80bdaa', fg='white', font='Arial 12', command=video_open).place(x=150, y=390)
Button(win, text='Extract Data', bg='#9d82cf', fg='white', font='Arial 12', command=on_extract).place(x=300, y=390)

win.mainloop()
