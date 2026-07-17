import time
import socket
import bluetooth # Если не установится, будем использовать стандартный socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- НАСТРОЙКИ СВЯЗИ ---
# Если автопоиск не сработает, впиши сюда MAC-адрес своего адаптера
TARGET_NAME = "OBDII" 
OBD_CMD = b"220003\r" # Твой запрос для K4M

class OBDConnection:
    def __init__(self):
        self.sock = None
        self.connected = False

    def connect(self):
        print("Поиск адаптера...")
        try:
            devices = bluetooth.discover_devices(duration=4, lookup_names=True)
            for addr, name in devices:
                if TARGET_NAME in name.upper() or "ELM" in name.upper():
                    print(f"Нашел: {name} [{addr}]. Подключаюсь...")
                    self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                    self.sock.connect((addr, 1))
                    self.sock.send(b"ATZ\r") # Сброс
                    time.sleep(1)
                    self.sock.send(b"ATSP5\r") # Протокол Renault/Nissan
                    self.connected = True
                    return True
        except Exception as e:
            print(f"Ошибка Bluetooth: {e}")
        return False

    def get_misfires(self):
        if not self.connected: return [0,0,0,0]
        try:
            self.sock.send(OBD_CMD)
            resp = self.sock.recv(1024).decode().strip()
            # Парсим ответ типа "62 00 03 XX"
            if "620003" in resp.replace(" ",""):
                val = int(resp.split()[-1], 16)
                return [val] * 4 # Раскладка по цилиндрам (пока общая)
        except: pass
        return [0,0,0,0]

# --- ПОДГОТОВКА ГРАФИКА ---
obd = OBDConnection()
obd.connect()

x_data = []
y_data = [[] for _ in range(4)]
gps_log = []
start_time = time.time()

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'] 
lines = [ax.plot([], [], label=f"Ц{i+1}", color=colors[i], lw=2)[0] for i in range(4)]

annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w", alpha=0.9),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

ax.set_ylim(-2, 100)
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)

def update(frame):
    curr_t = round(time.time() - start_time, 1)
    x_data.append(curr_t)
    
    # ПОЛУЧАЕМ РЕАЛЬНЫЕ ДАННЫЕ ВМЕСТО RANDOM
    misfires = obd.get_misfires()
    
    # Имитация GPS (в Pydroid можно добавить реальный GPS позже)
    gps_log.append((55.75, 37.61)) 

    for i in range(4):
        y_data[i].append(misfires[i])
        lines[i].set_data(x_data, y_data[i])

    status = " | ".join([f"Ц{i+1}:{v}" for i, v in enumerate(misfires)])
    ax.set_title(f"LIVE: {status}\nСтатус: {'СВЯЗЬ OK' if obd.connected else 'ПОИСК...'}")

    if plt.get_current_fig_manager().toolbar.mode == '':
        ax.set_xlim(curr_t - 30, curr_t + 5)
    return lines

def on_click(event):
    if event.inaxes == ax and len(x_data) > 0:
        ix = min(range(len(x_data)), key=lambda i: abs(x_data[i] - event.xdata))
        res = f"ВРЕМЯ: {x_data[ix]} сек\nЦ1-4: {y_data[0][ix]}\nКликни для деталей"
        annot.xy = (x_data[ix], event.ydata)
        annot.set_text(res)
        annot.set_visible(True)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', on_click)
ani = FuncAnimation(fig, update, interval=600, cache_frame_data=False)
plt.show()

