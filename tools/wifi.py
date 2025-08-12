import subprocess

def get_wifi_ssid():
    try:
        # Выполняем команду для получения информации о текущем подключении
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, encoding='utf-8')
        output = result.stdout

        # Ищем строку, содержащую SSID
        for line in output.split('\n'):
            if 'SSID' in line:
                ssid = line.split(':')[1].strip()
                return ssid
    except Exception as e:
        return str(e)

def get_wifi_password(ssid):
    try:
        # Выполняем команду для получения пароля Wi-Fi
        result = subprocess.run(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'], capture_output=True, text=True, encoding='utf-8')
        output = result.stdout

        # Выводим весь вывод для отладки
        print("Вывод команды netsh:")
        print(output)

        # Ищем строку, содержащую ключ
        for line in output.split('\n'):
            if 'Key Content' in line:
                password = line.split(':')[1].strip()
                return password
    except Exception as e:
        return str(e)

# Получаем SSID текущего подключения
ssid = get_wifi_ssid()
if ssid:
    # Получаем пароль для текущего SSID
    password = get_wifi_password(ssid)
    print(f"Пароль для SSID {ssid}: {password}")
else:
    print("Не удалось получить SSID текущего подключения.")