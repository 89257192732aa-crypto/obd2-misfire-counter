import time
import random
import socket
import bluetooth  # Нужна библиотека pybluez2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

class MisfireExpert(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        
        # Интерфейс
        self.add_widget(Label(text="SMART MISFIRE MONITOR", font_size='22sp', bold=True))
        self.info_lbl = Label(text="Статус: Нажмите ПОИСК", color=(1, 1, 0, 1), size_hint_y=0.1)
        self.add_widget(self.info_lbl)
        
        # Поля ввода
        self.engine_in = TextInput(text='K4M', multiline=False, size_hint_y=0.1)
        self.cyl_in = TextInput(text='4', multiline=False, size_hint_y=0.1)
        self.add_widget(self.engine_in)
        self.add_widget(self.cyl_in)

        # Вывод данных
        self.res_layout = BoxLayout(orientation='vertical')
        self.labels = []
        self.add_widget(self.res_layout)

        self.btn = Button(text="ПОИСК АДАПТЕРА И ЗАПУСК", size_hint_y=0.2, background_color=(0, 0.7, 0, 1))
        self.btn.bind(on_press=self.start_all)
        self.add_widget(self.btn)
        
        self.sock = None
        self.is_active = False

    def find_obd_mac(self):
        """Автоматический поиск MAC-адреса Bluetooth"""
        try:
            # Сканируем устройства 5 секунд
            devices = bluetooth.discover_devices(duration=5, lookup_names=True)
            for addr, name in devices:
                if "OBD" in name.upper() or "ELM" in name.upper():
                    return addr
        except: return None
        return None

    def start_all(self, instance):
        if not self.is_active:
            self.info_lbl.text = "Сканирую Bluetooth..."
            mac = self.find_obd_mac()
            
            if mac:
                try:
                    self.info_lbl.text = f"Подключаюсь к {mac}..."
                    # Создаем стандартный Bluetooth-сокет
                    self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                    self.sock.connect((mac, 1))
                    self.sock.send(b"ATZ\r") # Сброс
                    self.info_lbl.text = "СВЯЗЬ УСТАНОВЛЕНА!"
                except Exception as e:
                    self.info_lbl.text = "Ошибка порта. Включаю ДЕМО."
            else:
                self.info_lbl.text = "Адаптер не найден. ДЕМО-РЕЖИМ."
            
            self.setup_labels()
            self.is_active = True
            self.btn.text = "ОСТАНОВИТЬ"
            Clock.schedule_interval(self.update_ui, 0.5)
        else:
            self.stop_all()

    def setup_labels(self):
        self.res_layout.clear_widgets()
        self.labels = []
        count = int(self.cyl_in.text) if self.cyl_in.text.isdigit() else 4
        for i in range(count):
            lbl = Label(text=f"Цилиндр {i+1}: 0", font_size='26sp')
            self.labels.append(lbl)
            self.res_layout.add_widget(lbl)

    def update_ui(self, dt):
        for i, lbl in enumerate(self.labels):
            # Тут будет запрос: self.sock.send(b"220003\r")
            val = random.randint(0, 71) if i == 3 else random.randint(0, 5)
            lbl.text = f"Цилиндр {i+1}: {val}"

    def stop_all(self):
        self.is_active = False
        self.btn.text = "ПОИСК АДАПТЕРА И ЗАПУСК"
        Clock.unschedule(self.update_ui)
        if self.sock: self.sock.close()

class OBDApp(App):
    def build(self): return MisfireExpert()

if __name__ == "__main__":
    OBDApp().run()

# Для андроида 'pydroid 3'
