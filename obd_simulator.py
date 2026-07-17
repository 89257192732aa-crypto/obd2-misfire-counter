import time
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- ШАГ 1: ВВОД ДАННЫХ (ТО, ЧТО ТЫ ПРОСИЛ) ---
print("="*40)
print("   БОРТОВОЙ ДИАГНОСТИЧЕСКИЙ КОМПЛЕКС   ")
print("="*40)
engine_name = input("Введите модель двигателя (напр. K4M): ")
mileage = input("Введите текущий пробег (км): ")
print(f"\nЗапуск мониторинга для {engine_name}...")
print("ГРАФИК ОТКРОЕТСЯ В НОВОМ ОКНЕ")
print("="*40)

# --- ПОДГОТОВКА ДАННЫХ ---
x_data = []
y_data = [[] for _ in range(4)]
start_time = time.time()

# --- НАСТРОЙКА ГРАФИКА ---
fig, ax = plt.subplots(figsize=(10, 6))

# Цвета для цилиндров (4-й - красный, самый важный)
colors = ['blue', 'green', 'orange', 'red']
lines = []
for i in range(4):
    line, = ax.plot([], [], label=f"Цилиндр {i+1}", color=colors[i], 
                    linewidth=2.5 if i==3 else 1.5) # 4-й цилиндр толще
    lines.append(line)

# Заголовок с твоими данными
ax.set_title(f"Двигатель: {engine_name} | Пробег: {mileage} км", fontsize=14, fontweight='bold')
ax.set_xlabel("Время поездки (секунды)")
ax.set_ylabel("Пропуски (Misfires)")
ax.legend(loc="upper left")
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_ylim(-5, 100) # Шкала под твои 71 пропуск

def update(frame):
    # 1. Время
    current_time = time.time() - start_time
    x_data.append(current_time)
    
    # 2. ИМИТАЦИЯ ДАННЫХ (Твои 9, 31, 71)
    # Цилиндры 1-3 спокойные, 4-й иногда "поддает"
    misfires = [
        random.randint(0, 5), 
        random.randint(0, 3), 
        random.randint(0, 8), 
        random.randint(0, 75) if random.random() > 0.7 else random.randint(0, 10)
    ]
    
    for i in range(4):
        y_data[i].append(misfires[i])
        lines[i].set_data(x_data, y_data[i])

    # 3. ПЛАВНАЯ ПРОКРУТКА И "РУЧНИК"
    # Если ты НЕ нажал кнопку PAN (стрелочки) внизу, график едет сам
    toolbar = plt.get_current_fig_manager().toolbar
    if toolbar.mode == '':
        ax.set_xlim(current_time - 30, current_time + 5)
    
    return lines

# Запуск анимации (обновление каждые 500мс)
ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)

print("\nПОДСКАЗКА:")
print("1. В окне графика нажми на иконку 'Крестик из стрелок' (внизу).")
print("2. Теперь ТЯНИ график мышкой НАЗАД, чтобы посмотреть историю.")
print("3. Отожми кнопку, чтобы график снова 'поехал' вперед.")

plt.show()


