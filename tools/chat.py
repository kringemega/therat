import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import socket
import threading
import pyaudio
import numpy as np
import sounddevice as sd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        self.stream = self.p.open(format=pyaudio.paInt16, 
                                channels=1, 
                                rate=44100, 
                                input=True, 
                                frames_per_buffer=1024)

        self.update_plot()

    def update_plot(self):
        try:
            data = np.frombuffer(self.stream.read(1024), dtype=np.int16)
            data = data / 32768.0
            self.line.set_ydata(data)
            self.line.set_xdata(np.arange(len(data)))
            self.canvas.draw()
            
            if hasattr(self, 'connection'):
                try:
                    self.connection.sendall(data.tobytes())
                except (ConnectionError, OSError):
                    pass
            
            sd.play(data, 44100, blocking=False)
            
        except Exception as e:
            print("Audio error:", e)
        
        self.root.after(10, self.update_plot)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class ServerChat:
    def __init__(self, connection):
        self.root = tk.Toplevel()
        self.root.title("Server Chat")
        self.connection = connection
        
        self.chat_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20)
        self.chat_text.pack(padx=10, pady=10)
        
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_btn = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_btn.pack(padx=10, pady=5)
        
        self.start_receiver()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def send_message(self):
        message = self.entry.get()
        if message:
            self.chat_text.insert(tk.END, f"[Server]: {message}\n")
            try:
                self.connection.send(message.encode())
            except (ConnectionError, AttributeError):
                messagebox.showerror("Error", "No client connected")
            self.entry.delete(0, tk.END)
    
    def start_receiver(self):
        def receive_messages():
            while True:
                try:
                    msg = self.connection.recv(1024).decode()
                    if not msg:
                        break
                    self.chat_text.insert(tk.END, f"[Client]: {msg}\n")
                except ConnectionError:
                    self.chat_text.insert(tk.END, "Client disconnected\n")
                    break

        threading.Thread(target=receive_messages, daemon=True).start()
    
    def on_close(self):
        self.root.destroy()

class ServerApp:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 5555))
        self.server_socket.listen(1)
        
        self.server_vis_root = tk.Tk()
        self.server_vis_root.title("Server Control Panel")
        
        self.server_visualizer = MicrophoneVisualizer(self.server_vis_root)
        
        self.chat_btn = tk.Button(self.server_vis_root, text="Open Server Chat", 
                                 command=self.open_server_chat)
        self.chat_btn.pack(pady=10)
        
        self.connection = None
        self.server_chat = None
        
        self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_thread.start()
        
        self.server_vis_root.mainloop()

    def open_server_chat(self):
        if self.connection:
            if self.server_chat is None or not tk.Toplevel.winfo_exists(self.server_chat.root):
                self.server_chat = ServerChat(self.connection)
            else:
                self.server_chat.root.lift()
        else:
            messagebox.showinfo("Info", "No client connected yet")

    def accept_connections(self):
        while True:
            try:
                self.connection, addr = self.server_socket.accept()
                print("Client connected:", addr)
                self.server_visualizer.connection = self.connection
                
                if self.server_chat and tk.Toplevel.winfo_exists(self.server_chat.root):
                    self.server_chat.connection = self.connection
                
            except OSError as e:
                print("Server accept error:", e)
                break

class ClientApp:
    def __init__(self, server_ip='localhost'):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, 5555))
            
            self.client_root = tk.Tk()
            self.client_root.title("Client Application")
            
            self.chat_frame = tk.Frame(self.client_root)
            self.chat_frame.pack(pady=10)
            
            self.chat_text = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, width=50, height=15)
            self.chat_text.pack(padx=10, pady=5)
            
            self.entry = tk.Entry(self.chat_frame, width=50)
            self.entry.pack(padx=10, pady=5)
            self.entry.bind("<Return>", lambda e: self.send_message())
            
            self.send_btn = tk.Button(self.chat_frame, text="Send", command=self.send_message)
            self.send_btn.pack(padx=10, pady=5)
            
            self.visualizer_frame = tk.Frame(self.client_root)
            self.visualizer_frame.pack(pady=10)
            
            self.client_visualizer = MicrophoneVisualizer(self.visualizer_frame)
            self.client_visualizer.connection = self.client_socket
            
            self.start_receiver()
            self.client_root.mainloop()
            
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to server")
        except Exception as e:
            messagebox.showerror("Error", f"Client error: {e}")

    def send_message(self):
        message = self.entry.get()
        if message:
            self.chat_text.insert(tk.END, f"[You]: {message}\n")
            try:
                self.client_socket.send(message.encode())
            except ConnectionError:
                messagebox.showerror("Error", "Connection to server lost")
            self.entry.delete(0, tk.END)

    def start_receiver(self):
        def receive_messages():
            while True:
                try:
                    msg = self.client_socket.recv(1024).decode()
                    if not msg:
                        break
                    self.chat_text.insert(tk.END, f"[Server]: {msg}\n")
                except ConnectionError:
                    self.chat_text.insert(tk.END, "Disconnected from server\n")
                    break

        threading.Thread(target=receive_messages, daemon=True).start()

def start_as_server():
    ServerApp()

def start_as_client():
    server_ip = simpledialog.askstring("Server IP", "Enter server IP address:", initialvalue="localhost")
    if server_ip:
        ClientApp(server_ip)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    choice = messagebox.askquestion("Select Mode", "Run as server?", icon='question')
    if choice == 'yes':
        start_as_server()
    else:
        start_as_client()