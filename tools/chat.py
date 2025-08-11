import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import pyaudio
import numpy as np
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

def start_client_chat():
    root = tk.Tk()
    root.title("Client Chat")
    root.geometry("400x300")
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing

    chat_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
    chat_text.pack(padx=10, pady=10)

    def send_message():
        message = entry.get()
        chat_text.insert(tk.END, f"[Client]: {message}\n")
        client_socket.send(message.encode())
        entry.delete(0, tk.END)

    entry = tk.Entry(root, width=50)
    entry.pack(padx=10, pady=10)
    entry.bind("<Return>", lambda event: send_message())

    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack(padx=10, pady=10)

    def receive_messages():
        while True:
            try:
                message = client_socket.recv(4096).decode()
                if not message:
                    break
                chat_text.insert(tk.END, f"[Server]: {message}\n")
            except (ConnectionResetError, BrokenPipeError):
                break

    threading.Thread(target=receive_messages, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5555))

    root = tk.Tk()
    app = MicrophoneVisualizer(root)
    start_client_chat()
    root.mainloop()