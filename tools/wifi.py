import subprocess
import re

def get_wifi_passwords():
    """Получает все сохранённые Wi-Fi сети и их пароли."""
    try:
        # Получаем список всех Wi-Fi профилей
        profiles_output = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        
        profiles = re.findall(r"Все профили пользователей\s*:\s(.*)", profiles_output)
        if not profiles:
            return {"error": "No Wi-Fi profiles found."}
        
        wifi_data = {}
        for profile in profiles:
            profile = profile.strip()
            if not profile:
                continue
            
            # Получаем пароль для каждого профиля
            password_output = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            password_match = re.search(r"Содержимое ключа\s*:\s(.*)", password_output)
            password = password_match.group(1).strip() if password_match else "No password"
            wifi_data[profile] = password
        
        return wifi_data
    
    except Exception as e:
        return {"error": f"Failed to get Wi-Fi passwords: {str(e)}"}

# Пример использования (можно вызвать из server.py)
if __name__ == "__main__":
    wifi_passwords = get_wifi_passwords()
    for wifi, password in wifi_passwords.items():
        print(f"Wi-Fi: {wifi}\nPassword: {password}\n")