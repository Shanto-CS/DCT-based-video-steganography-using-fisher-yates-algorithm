import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from pathlib import Path

class Steganography:
    def __init__(self):
        self.frame_size = (640, 480)  # Default frame size
        self.bits_per_channel = 4  # Using 4 bits per channel for better quality
        
    def embed_data(self, video_path, image_path, output_path, progress_callback):
        try:
            # Open video and image
            video = cv2.VideoCapture(video_path)
            secret_img = cv2.imread(image_path)
            
            # Get video properties
            fps = int(video.get(cv2.CAP_PROP_FPS))
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Resize secret image to match frame size
            secret_img = cv2.resize(secret_img, self.frame_size)
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, self.frame_size)
            
            frames_processed = 0
            mask = 2 ** self.bits_per_channel - 1  # Create bit mask for embedding
            
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break
                    
                # Resize frame to match desired size
                frame = cv2.resize(frame, self.frame_size)
                
                # Embed secret image data into multiple bits of video frame
                if frames_processed == 0:  # Embed in first frame only
                    for i in range(3):  # For each color channel
                        # Clear the target bits in the frame
                        frame[:,:,i] = frame[:,:,i] & (0xFF << self.bits_per_channel)
                        
                        # Shift the secret image bits to the right position
                        secret_bits = (secret_img[:,:,i] >> (8 - self.bits_per_channel)) & mask
                        
                        # Embed the secret bits
                        frame[:,:,i] = frame[:,:,i] | secret_bits
                
                out.write(frame)
                frames_processed += 1
                
                # Update progress
                progress = (frames_processed / frame_count) * 100
                progress_callback(progress)
            
            video.release()
            out.release()
            return True
            
        except Exception as e:
            raise Exception(f"Embedding failed: {str(e)}")
            
    def extract_data(self, stego_video_path, output_path, progress_callback):
        try:
            # Open stego video
            video = cv2.VideoCapture(stego_video_path)
            
            # Read first frame
            ret, frame = video.read()
            if not ret:
                raise Exception("Could not read video file")
                
            # Resize frame if necessary
            frame = cv2.resize(frame, self.frame_size)
            
            # Extract hidden image from multiple bits
            extracted_img = np.zeros(frame.shape, dtype=np.uint8)
            mask = 2 ** self.bits_per_channel - 1  # Create bit mask for extraction
            
            for i in range(3):  # For each color channel
                # Extract the bits containing the hidden data
                extracted_bits = frame[:,:,i] & mask
                
                # Shift the bits to their proper position
                extracted_img[:,:,i] = extracted_bits << (8 - self.bits_per_channel)
                
                # Optional: Improve perceived quality by spreading the values
                if self.bits_per_channel < 8:
                    # Replicate the extracted bits to fill the remaining bits
                    for j in range(8 - self.bits_per_channel):
                        extracted_img[:,:,i] |= extracted_bits << j
            
            # Apply subtle smoothing to reduce potential noise
            extracted_img = cv2.GaussianBlur(extracted_img, (3, 3), 0.5)
            
            # Enhance contrast
            lab = cv2.cvtColor(extracted_img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge((l,a,b))
            extracted_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Save extracted image
            cv2.imwrite(output_path, extracted_img)
            
            video.release()
            progress_callback(100)  # Operation complete
            return True
            
        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("High Quality Steganography Tool")
        self.steg = Steganography()
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create frames
        self.embed_frame = ttk.Frame(self.notebook)
        self.extract_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.embed_frame, text="Embed")
        self.notebook.add(self.extract_frame, text="Extract")
        
        self.setup_embed_frame()
        self.setup_extract_frame()
        
    def setup_embed_frame(self):
        # Quality selection
        ttk.Label(self.embed_frame, text="Image Quality (bits per channel):").pack(pady=5)
        self.quality_var = tk.StringVar(value="4")
        quality_combo = ttk.Combobox(self.embed_frame, 
                                   textvariable=self.quality_var,
                                   values=["2", "3", "4", "5", "6"],
                                   state="readonly",
                                   width=5)
        quality_combo.pack(pady=5)
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)
        
        # Video selection
        ttk.Label(self.embed_frame, text="Select Video File:").pack(pady=5)
        video_button = ttk.Button(self.embed_frame, text="Choose Video", 
                                command=self.choose_video)
        video_button.pack(pady=5)
        
        # Image selection
        ttk.Label(self.embed_frame, text="Select Image to Hide:").pack(pady=5)
        image_button = ttk.Button(self.embed_frame, text="Choose Image", 
                                command=self.choose_image)
        image_button.pack(pady=5)
        
        # Embed button
        embed_button = ttk.Button(self.embed_frame, text="Embed", 
                                command=self.on_embed)
        embed_button.pack(pady=10)
        
        # Progress bar
        self.embed_progress = ttk.Progressbar(
            self.embed_frame,
            mode='determinate',
            length=300
        )
        self.embed_progress.pack(pady=10)
        
    def setup_extract_frame(self):
        # Stego video selection
        ttk.Label(self.extract_frame, text="Select Stego Video:").pack(pady=5)
        stego_button = ttk.Button(self.extract_frame, text="Choose Video", 
                                command=self.choose_stego_video)
        stego_button.pack(pady=5)
        
        # Extract button
        extract_button = ttk.Button(self.extract_frame, text="Extract", 
                                  command=self.on_extract)
        extract_button.pack(pady=10)
        
        # Progress bar
        self.extract_progress = ttk.Progressbar(
            self.extract_frame,
            mode='determinate',
            length=300
        )
        self.extract_progress.pack(pady=10)
        
        # Frame for preview
        self.preview_frame = ttk.Frame(self.extract_frame)
        self.preview_frame.pack(pady=10)
        
    def on_quality_change(self, event):
        self.steg.bits_per_channel = int(self.quality_var.get())
        
    def choose_video(self):
        self.open_video_file = filedialog.askopenfilename(
            filetypes=(('MP4 files', '*.mp4'), ('All files', '*.*')))
            
    def choose_image(self):
        self.open_image_file = filedialog.askopenfilename(
            filetypes=(('Image files', '*.png *.jpg *.jpeg'), ('All files', '*.*')))
            
    def choose_stego_video(self):
        self.stego_video_file = filedialog.askopenfilename(
            filetypes=(('MP4 files', '*.mp4'), ('All files', '*.*')))
    
    def update_progress(self, progress_bar, value):
        """Update progress bar value"""
        progress_bar['value'] = value
        self.root.update_idletasks()
    
    def on_embed(self):
        if not (hasattr(self, 'open_video_file') and hasattr(self, 'open_image_file')):
            messagebox.showerror("Error", "Please select both video and image files.")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=(('MP4 files', '*.mp4'),))
            
        if output_path:
            try:
                # Reset progress bar
                self.embed_progress['value'] = 0
                
                def progress_callback(value):
                    self.update_progress(self.embed_progress, value)
                
                success = self.steg.embed_data(
                    self.open_video_file, 
                    self.open_image_file,
                    output_path,
                    progress_callback
                )
                if success:
                    messagebox.showinfo("Success", "Data embedded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def on_extract(self):
        if not hasattr(self, 'stego_video_file'):
            messagebox.showerror("Error", "Please select a stego video file.")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=(('PNG files', '*.png'), ('JPG files', '*.jpg')))
            
        if output_path:
            try:
                # Reset progress bar
                self.extract_progress['value'] = 0
                
                def progress_callback(value):
                    self.update_progress(self.extract_progress, value)
                
                success = self.steg.extract_data(
                    self.stego_video_file,
                    output_path,
                    progress_callback
                )
                if success:
                    messagebox.showinfo("Success", "Image extracted successfully!")
                    # Show extracted image preview
                    img = Image.open(output_path)
                    img = img.resize((150, 150), Image.LANCZOS)
                    thumbnail = ImageTk.PhotoImage(img)
                    
                    # Clear previous preview if exists
                    for widget in self.preview_frame.winfo_children():
                        widget.destroy()
                        
                    # Add new preview
                    preview_label = ttk.Label(self.preview_frame, text="Extracted Image:")
                    preview_label.pack()
                    extracted_preview = ttk.Label(self.preview_frame, image=thumbnail)
                    extracted_preview.image = thumbnail
                    extracted_preview.pack()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    root.geometry("500x600")
    app = SteganographyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()