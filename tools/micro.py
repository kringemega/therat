import tkinter as tk
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket
import sounddevice as sd

class MicrophoneVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Microphone Visualizer")

        self.figure, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1024)
        self.ax.set_ylabel('Amplitude')
        self.ax.set_xlabel('Sample')

        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5555))

        self.update_plot()

    def update_plot(self):
        data = np.frombuffer(self.stream.read(1024), dtype=np.int16)
        data = data / 32768.0  # Normalize to range [-1, 1]
        self.line.set_ydata(data)
        self.line.set_xdata(np.arange(len(data)))
        self.canvas.draw()

        # Send data to server
        self.client_socket.sendall(data.tobytes())

        # Play back the audio data
        sd.play(data, 44100, 1)

        self.root.after(10, self.update_plot)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.client_socket.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = MicrophoneVisualizer(root)
    root.mainloop()