import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os
from colorama import Fore
import ctypes

clients = {}

def logo():
    print(f"{Fore.GREEN}███████╗██████╗░░█████╗░████████╗")
    print(f"{Fore.GREEN}██╔════╝██╔══██╗██╔══██╗╚══██╔══╝")
    print(f"{Fore.GREEN}█████╗░░██████╔╝███████║░░░██║░░░")
    print(f"{Fore.GREEN}██╔══╝░░██╔══██╗██╔══██║░░░██║░░░")
    print(f"{Fore.GREEN}██║░░░░░██║░░██║██║░░██║░░░██║░░░   ")
    print(f"{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░")
    print(f"{Fore.GREEN}{Fore.RESET}")

def handle_client(client_socket, addr):
    clients[addr] = client_socket
    ctypes.windll.kernel32.SetConsoleTitleW(f"FRAT | CONNECTED CLIENTS: {len(clients)}")

    def receive_messages():
        while True:
            try:
                message = client_socket.recv(4096).decode()
                if not message:
                    break
                if chat_window:
                    chat_text.insert(tk.END, f"[Client {addr[0]}]: {message}\n")
            except (ConnectionResetError, BrokenPipeError):
                break

        print(f"\n{Fore.RED}[!] {Fore.RESET} | Client {addr[0]} disconnected.")
        client_socket.close()
        del clients[addr]

    threading.Thread(target=receive_messages, daemon=True).start()

def accept_clients(server):
    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

def start_server(host="0.0.0.0", port=5555):
    global chat_window, chat_text
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    threading.Thread(target=accept_clients, args=(server,), daemon=True).start()
    os.system("cls")
    logo()
    print(f"[{Fore.YELLOW}?{Fore.RESET}] Waiting for clients to connect...")

    chat_window = None
    chat_text = None

    while True:
        command = input("Enter command (or 'chat' to open chat): ")
        if command.lower() == "chat":
            if not clients:
                print("No clients connected.")
                continue
            print("\n[Connected Clients]")
            for idx, addr in enumerate(clients.keys(), start=1):
                print(f"{idx}. {addr[0]}:{addr[1]}")
            try:
                choice = int(input("\nSelect client number: ")) - 1
                if 0 <= choice < len(clients):
                    target_addr = list(clients.keys())[choice]
                    if not chat_window:
                        chat_window = tk.Tk()
                        chat_window.title("Server Chat")
                        chat_window.geometry("400x300")
                        chat_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing

                        chat_text = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD, width=40, height=10)
                        chat_text.pack(padx=10, pady=10)

                        def send_message():
                            message = entry.get()
                            chat_text.insert(tk.END, f"[Server]: {message}\n")
                            clients[target_addr].send(message.encode())
                            entry.delete(0, tk.END)

                        entry = tk.Entry(chat_window, width=50)
                        entry.pack(padx=10, pady=10)
                        entry.bind("<Return>", lambda event: send_message())

                        send_button = tk.Button(chat_window, text="Send", command=send_message)
                        send_button.pack(padx=10, pady=10)

                        # Send chat command to the selected client
                        clients[target_addr].send("chat".encode())

                        chat_window.mainloop()
                    else:
                        print("Chat window is already open.")
                else:
                    print("Invalid selection: client number out of range")
            except ValueError:
                print("Invalid input: please enter a number")
        elif command.lower() == "exit":
            break
        else:
            print("Unknown command.")

    server.close()

if __name__ == "__main__":
    start_server()