import serial
import time
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- 1. ВВОД ДАННЫХ ---
print("="*50)
print("   DIAGNOSTIC SYSTEM: ALMERA G15 (K4M)   ")
print("="*50)
engine_model = input("Модель двигателя: ")
mileage = input("Текущий пробег (км): ")
port_name = input("Введите COM-порт (напр. COM3): ").upper()

# --- 2. НАСТРОЙКА СВЯЗИ (Версия 1.5) ---
try:
    # Для версии 1.5 обычно 38400, если USB — попробуй 115200
    ser = serial.Serial(port_name, 38400, timeout=1)
    time.sleep(2)
    
    # Инициализация командами AT
    ser.write(b"ATZ\r")      # Сброс адаптера
    time.sleep(1)
    ser.write(b"ATE0\r")     # Отключить эхо
    ser.write(b"ATSP5\r")    # ЖЕСТКИЙ ПРОТОКОЛ KWP FAST (для Renault/Nissan)
    time.sleep(1)
    
    print(f"--- СВЯЗЬ С ADAPTER v1.5 УСТАНОВЛЕНА ---")
except Exception as e:
    print(f"ОШИБКА ПОРТА: {e}. Проверь номер COM или закрой другие программы!")
    input("Нажми Enter для выхода...")
    exit()

# --- 3. ПОДГОТОВКА ГРАФИКА ---
x_data, y_data = [], [[] for _ in range(4)]
start_time = time.time()

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'] # 4-й — красный
lines = [ax.plot([], [], label=f"Цилиндр {i+1}", color=colors[i], 
         linewidth=3.0 if i==3 else 1.5)[0] for i in range(4)]

ax.set_title(f"Мониторинг: {engine_model} | Пробег: {mileage} км", fontsize=14, fontweight='bold')
ax.set_xlabel("Время поездки (сек)")
ax.set_ylabel("Счетчик пропусков (Misfires)")
ax.legend(loc="upper left")
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_ylim(-5, 100) # Твой пик был 71, ставим 100

def get_ecu_data():
    """Запрос данных пропусков из ЭБУ"""
    try:
        # Прямой запрос счетчика пропусков для Valeo/EMS
        ser.write(b"220003\r") 
        raw = ser.readline().decode('utf-8', errors='ignore')
        
        if "62 00 03" in raw:
            # Парсим последний байт (твои 9, 31, 71)
            val = int(raw.split()[-1], 16)
            return [val] * 4 # Общий счетчик на все линии
        return [0, 0, 0, 0]
    except:
        return [0, 0, 0, 0]

def update(frame):
    current_time = time.time() - start_time
    x_data.append(current_time)
    
    misfires = get_ecu_data()
    for i in range(4):
        y_data[i].append(misfires[i])
        lines[i].set_data(x_data, y_data[i])

    # АВТОПРОКРУТКА И "РУЧНИК"
    # Если нажат "Крестик" (Pan) внизу, график замирает для просмотра истории
    if plt.get_current_fig_manager().toolbar.mode == '':
        ax.set_xlim(current_time - 40, current_time + 5)
    
    return lines

ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)

print("\nГРАФИК ЗАПУЩЕН!")
print("- Чтобы мотать историю назад: нажми кнопку со стрелками (Pan) внизу.")
print("- Чтобы вернуть автопрокрутку: отожми кнопку.")

plt.show()
ser.close()

