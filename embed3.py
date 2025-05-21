from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

win = Tk()
win.geometry('600x500')
win.config(bg='#e6dfcc')

# Global variables for file paths
open_video_file = None
open_image_file = None
video_thumbnail = None

# Open video file and preview a frame
def video_open():
    global open_video_file, video_thumbnail
    open_video_file = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Video File',
                                                 filetypes=(('MP4 files', '*.mp4'), ('All Files', '*.*')))
    if open_video_file:
        cap = cv2.VideoCapture(open_video_file)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((150, 150), Image.LANCZOS)
            video_thumbnail = ImageTk.PhotoImage(frame)
            video_label.configure(image=video_thumbnail)
            video_label.image = video_thumbnail
            Label(win, text="Video Loaded", bg="#e6dfcc", font=("Arial", 10)).place(x=20, y=320)

# Open image file for embedding
def img_open():
    global open_image_file
    open_image_file = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Image File',
                                                 filetypes=(('PNG files', '*.png'), ('JPG files', '*.jpg')))
    if open_image_file:
        img = Image.open(open_image_file)
        img = img.resize((64, 64), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        img_label.configure(image=img)
        img_label.image = img
        Label(win, text="Image Loaded", bg="#e6dfcc", font=("Arial", 10)).place(x=200, y=320)

# Embed image in video with improved quality
def embed_data_in_video(video_path, image_path, output_path):
    cap = cv2.VideoCapture(video_path)
    secret_image = Image.open(image_path).convert("RGB")
    secret_image = secret_image.resize((64, 64))  # Resize for embedding
    secret_data = np.array(secret_image)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    frame_index = 0
    max_frames = 64  # Number of frames to embed the entire image
    while cap.isOpened() and frame_index < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        y_channel = yuv_frame[:, :, 0]

        row = secret_data[frame_index]
        dct_frame = cv2.dct(np.float32(y_channel) / 255.0)

        for i, pixel in enumerate(row):
            dct_frame[4, i] += pixel[0] / 255.0  # R
            dct_frame[5, i] += pixel[1] / 255.0  # G
            dct_frame[6, i] += pixel[2] / 255.0  # B

        modified_y_channel = cv2.idct(dct_frame) * 255.0
        modified_y_channel = np.clip(modified_y_channel, 0, 255).astype(np.uint8)
        yuv_frame[:, :, 0] = modified_y_channel
        modified_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR)

        out.write(modified_frame)
        frame_index += 1

    # Continue writing remaining frames without modification
    while ret:
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    cap.release()
    out.release()
    messagebox.showinfo("Success", "Data embedded and video saved as " + output_path)

# GUI Components
Label(win, text='Video Steganography', font='impack 20 bold', fg='black', bg='#e6dfcc').pack(pady=10)

img_label = Label(win, bg='#a8a7a3')
img_label.place(x=20, y=100)
video_label = Label(win, bg='#a8a7a3')
video_label.place(x=200, y=100)

Button(win, text='Open Video', bg='#80bdaa', fg='white', font='Arial 12', cursor='hand2', command=video_open).place(x=20, y=390)
Button(win, text='Open Image', bg='#80bdaa', fg='white', font='Arial 12', cursor='hand2', command=img_open).place(x=150, y=390)
Button(win, text='Embed Data', bg='#9d82cf', fg='white', font='Arial 12', cursor='hand2', command=lambda: embed_data_in_video(open_video_file, open_image_file, 'stego_video.mp4')).place(x=300, y=390)

win.mainloop()
