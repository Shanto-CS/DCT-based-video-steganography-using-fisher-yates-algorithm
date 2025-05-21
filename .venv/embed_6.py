from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from scipy.fftpack import dct, idct
import random
import os

# Fisher-Yates shuffle function
def fisher_yates_shuffle(data, seed):
    random.seed(seed)
    for i in range(len(data) - 1, 0, -1):
        j = random.randint(0, i)
        data[i], data[j] = data[j], data[i]
    return data

# Embedding function
def embed_data_in_video(video_path, image_path, output_path):
    cap = cv2.VideoCapture(video_path)
    secret_image = Image.open(image_path).convert("RGB")
    secret_image = secret_image.resize((512, 512))  # Adjust the size here as needed
    secret_data = np.array(secret_image)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    shuffle_indices = fisher_yates_shuffle(list(range(frame_count)), 42)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        y_channel = yuv_frame[:, :, 0]

        if frame_index in shuffle_indices[:1]:  # Embed in the first frame
            dct_frame = cv2.dct(np.float32(y_channel) / 255.0)
            for i in range(512):
                for j in range(512):
                    dct_frame[i % 64, j % 64] += secret_data[i, j, 0] / 255.0  # Embed R channel

            modified_y_channel = cv2.idct(dct_frame) * 255.0
            yuv_frame[:, :, 0] = np.clip(modified_y_channel, 0, 255).astype(np.uint8)
            modified_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR)
        else:
            modified_frame = frame

        out.write(modified_frame)
        frame_index += 1

    cap.release()
    out.release()
    messagebox.showinfo("Success", "Data embedded and video saved as " + output_path)

# GUI setup
win = Tk()
win.geometry('800x500')
win.config(bg='#e6dfcc')

open_video_file = None
open_image_file = None
video_thumbnail = None

# Open video function
def video_open():
    global open_video_file, video_thumbnail
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

# Open image function
def img_open():
    global open_image_file
    open_image_file = filedialog.askopenfilename(filetypes=(('PNG files', '*.png'), ('JPG files', '*.jpg')))
    if open_image_file:
        img = Image.open(open_image_file).resize((150, 150), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        img_label.configure(image=img)
        img_label.image = img

# Embed data button action
def on_embed():
    if open_video_file and open_image_file:
        embed_data_in_video(open_video_file, open_image_file, 'stego_video.mp4')
    else:
        messagebox.showerror("Error", "Please select both video and image files.")

# GUI components
Label(win, text='Video Steganography', font='impact 20 bold', fg='black', bg='#e6dfcc').pack(pady=10)
img_label = Label(win, bg='#a8a7a3')
img_label.place(x=20, y=100)
video_label = Label(win, bg='#a8a7a3')
video_label.place(x=200, y=100)

Button(win, text='Open Video', bg='#80bdaa', fg='white', font='Arial 12', command=video_open).place(x=20, y=390)
Button(win, text='Open Image', bg='#80bdaa', fg='white', font='Arial 12', command=img_open).place(x=150, y=390)
Button(win, text='Embed Data', bg='#9d82cf', fg='white', font='Arial 12', command=on_embed).place(x=300, y=390)

win.mainloop()
