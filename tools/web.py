import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Open video capture (0 is usually the default webcam)
        self.vid = cv2.VideoCapture(0)
        
        if not self.vid.isOpened():
            raise ValueError("Unable to open webcam")
        
        # Create a canvas that can fit the video source
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), 
                               height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()
        
        # Button to capture image
        self.btn_capture = ttk.Button(window, text="Capture", command=self.capture)
        self.btn_capture.pack(pady=10)
        
        # Button to toggle fullscreen
        self.btn_fullscreen = ttk.Button(window, text="Toggle Fullscreen", command=self.toggle_fullscreen)
        self.btn_fullscreen.pack(pady=5)
        
        # Button to exit
        self.btn_exit = ttk.Button(window, text="Exit", command=self.close)
        self.btn_exit.pack(pady=5)
        
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        
        self.fullscreen = False
        self.window.mainloop()
    
    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.read()
        
        if ret:
            # Convert to RGB and then to ImageTk format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            
            # Update the canvas with the new image
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        self.window.after(self.delay, self.update)
    
    def capture(self):
        # Capture a frame from the video source
        ret, frame = self.vid.read()
        
        if ret:
            # Save the captured image
            cv2.imwrite("captured_image.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            print("Image captured as captured_image.jpg")
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)
    
    def close(self):
        # Release the video source when closing
        if self.vid.isOpened():
            self.vid.release()
        self.window.destroy()

# Create a window and pass it to the WebcamApp class
root = tk.Tk()
app = WebcamApp(root, "Webcam Viewer")