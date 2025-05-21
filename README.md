# Video Steganography Thesis Project

## Overview

This project is the implementation of my thesis on **Video Steganography**, focusing on hiding images inside video files using Least Significant Bit (LSB) techniques. The tool provides a user-friendly GUI for embedding and extracting images, demonstrating the practical application of steganography for secure data hiding.

---

## Table of Contents

- [Introduction](#introduction)
- [Functionality](#functionality)
- [How It Works](#how-it-works)
- [Statistics & Results](#statistics--results)
- [Usage Instructions](#usage-instructions)
- [Project Structure](#project-structure)
- [Conclusion](#conclusion)

---

## Introduction

Steganography is the art of hiding information within other non-secret data. In this project, an image is hidden inside a video file by modifying the least significant bits of the video frames. This approach ensures that the hidden data is imperceptible to the human eye, making it a powerful tool for secure communication.

---

## Functionality

- **Embed Image in Video:**  
  Select a video and an image. The tool embeds the image into the first frame of the video using LSB manipulation.
- **Extract Image from Video:**  
  Select a stego video. The tool extracts the hidden image from the first frame and saves it as a separate file.
- **Progress Tracking:**  
  Progress bars show the status of embedding and extraction.
- **Image Preview:**  
  After extraction, a preview of the hidden image is displayed in the GUI.
- **Error Handling:**  
  User-friendly error messages for invalid files or process failures.

---

## How It Works

### Embedding Process

1. **Input Selection:**  
   User selects a video file and an image file.
2. **Resizing:**  
   The image is resized to match the video frame size (default: 640x480).
3. **LSB Embedding:**  
   The most significant bit of each image pixel is embedded into the least significant bit of the corresponding video frame pixel (for all color channels, in the first frame).
4. **Video Output:**  
   The modified frames are saved as a new video file.

### Extraction Process

1. **Input Selection:**  
   User selects a stego video file.
2. **LSB Extraction:**  
   The tool reads the first frame and reconstructs the hidden image by extracting the least significant bit from each pixel.
3. **Image Output:**  
   The extracted image is saved and previewed.

---

## Statistics & Results

- **Imperceptibility:**  
  The visual quality of the video remains almost unchanged after embedding, as only the least significant bits are altered.
- **Capacity:**  
  The maximum size of the hidden image is limited by the frame size (e.g., 640x480 pixels).
- **Robustness:**  
  The method is robust against casual viewing but not against heavy video compression or editing.
- **Performance:**  
  - Embedding and extraction are fast for standard video sizes.
  - Progress bars provide real-time feedback.

**Example Results:**
- **Test Video:** 640x480, 30fps, 10 seconds
- **Hidden Image:** 640x480 PNG
- **Embedding Time:** ~2 seconds
- **Extraction Time:** <1 second
- **Visual Quality Loss:** None perceptible to the human eye

---

## Usage Instructions

1. **Run the Application:**  
   ```
   python FINAL.py
   ```
2. **Embed Tab:**  
   - Click "Choose Video" and select an MP4 file.
   - Click "Choose Image" and select a PNG/JPG image.
   - Click "Embed" and choose a save location for the stego video.
   - Wait for the progress bar to complete.
3. **Extract Tab:**  
   - Click "Choose Video" and select a stego video.
   - Click "Extract" and choose a save location for the extracted image.
   - The extracted image will be previewed in the GUI.

---

## Project Structure

- `FINAL.py` — Main application with GUI and LSB steganography logic.
- `main.py`, `embed_8c.py` — Other experimental or advanced methods (e.g., DCT-based).
- `README.md` — Project documentation.

---

## Conclusion

This project demonstrates a practical and efficient method for hiding images in video files using LSB steganography. The tool is easy to use, provides real-time feedback, and preserves the visual quality of the video. It serves as a foundation for further research and development in secure data hiding and steganographic techniques.

---

**For academic or demonstration purposes only. For secure or production use, consider more advanced and robust steganographic methods.**