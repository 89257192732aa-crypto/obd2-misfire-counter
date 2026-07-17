import serial
import time

# Укажи свой порт (например, 'COM3' для Windows или '/dev/rfcomm0' для Android/Linux)
PORT = 'COM3' 
BAUD = 38400

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"--- Подключено к Альмере на порту {PORT} ---")
except:
    print("Ошибка: Не могу открыть порт. Закрой Car Scanner!")
    exit()

def cmd(command):
    ser.write((command + '\r').encode())
    time.sleep(0.1)
    return ser.read_all().decode(errors='ignore')

# 1. Настройка адаптера (Инициализация)
cmd('ATZ')      # Сброс
cmd('ATE0')     # Эхо выкл (чтобы не дублировал команды в ответе)
cmd('ATSP0')    # Протокол авто
cmd('ATH1')     # Включить заголовки (чтобы видеть кто отвечает)

print("Мониторинг запущен... Нажми Ctrl+C для выхода")

# 2. Основной цикл
# Для Almera G15 (K4M) пробуем запрос 06 по стандарту или спец. адрес
# Команда "06 00" запрашивает доступные тесты мониторинга
# Команда "22 00 03" часто является счетчиком пропусков на Renault/Nissan
QUERY = "22 00 03" 

try:
    last_val = 0
    while True:
        response = cmd(QUERY)
        
        # Логика обработки ответа (пример ответа: "62 00 03 00 47")
        # 00 47 в HEX — это 71 в десятичной системе.
        if "62 00 03" in response:
            try:
                # Очищаем ответ от лишних символов и берем последние 2 байта
                clean_hex = response.split("62 00 03")[1].replace(" ", "").strip()[:4]
                current_misfires = int(clean_hex, 16)
                
                # Эффект "бегающих" цифр:
                if current_misfires > last_val:
                    print(f"!!! ПРОПУСК: {current_misfires} (всего выросло на {current_misfires - last_val})")
                elif current_misfires < last_val:
                    print(f"Счетчик сброшен/уменьшен: {current_misfires}")
                else:
                    print(f"Стабильно: {current_misfires}", end='\r')
                
                last_val = current_misfires
            except:
                pass
        
        time.sleep(0.5) # Частота опроса (2 раза в секунду)

except KeyboardInterrupt:
    ser.close()
    print("\nМониторинг остановлен.")
