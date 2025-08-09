import tkinter as tk
from tkinter import ttk
import pyautogui
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import cv2
class MultiMonitorApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Настройки
        self.running = True
        self.update_delay = 30  # ms
        
        # Получаем информацию о мониторах
        self.monitors = self.get_monitors_info()
        self.num_monitors = len(self.monitors)
        
        if self.num_monitors == 0:
            raise ValueError("Не обнаружено подключенных мониторов")
        
        # Создаем фреймы для отображения
        self.main_frame = ttk.Frame(window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем канвасы для каждого монитора
        self.monitor_canvases = []
        self.monitor_frames = []
        
        for i in range(self.num_monitors):
            frame = ttk.LabelFrame(self.main_frame, text=f"Монитор {i+1}")
            frame.pack(side=tk.LEFT if i == 0 else tk.RIGHT, 
                      padx=10, pady=10, 
                      fill=tk.BOTH, expand=True)
            self.monitor_frames.append(frame)
            
            canvas = tk.Canvas(frame)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.monitor_canvases.append(canvas)
        
        # Панель управления
        self.control_frame = ttk.Frame(window)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_capture_all = ttk.Button(self.control_frame, 
                                        text="Снять все экраны", 
                                        command=self.capture_all_screens)
        self.btn_capture_all.pack(side=tk.LEFT, padx=5)
        
        for i in range(self.num_monitors):
            btn = ttk.Button(self.control_frame, 
                           text=f"Снять монитор {i+1}", 
                           command=lambda idx=i: self.capture_single_screen(idx))
            btn.pack(side=tk.LEFT, padx=5)
        
        self.btn_exit = ttk.Button(self.control_frame, text="Выход", command=self.close)
        self.btn_exit.pack(side=tk.RIGHT, padx=5)
        
        # Запуск потока обновления
        self.update_thread = threading.Thread(target=self.update_screens, daemon=True)
        self.update_thread.start()
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.mainloop()
    
    def get_monitors_info(self):
        """Получаем информацию о мониторах"""
        try:
            # Простое определение количества мониторов
            return [{'index': i} for i in range(pyautogui.screenshot().size[0] // pyautogui.size()[0])] or [{'index': 0}]
        except:
            return [{'index': 0}]
    
    def update_screens(self):
        """Обновляем изображения на всех мониторах"""
        while self.running:
            try:
                # Получаем размеры всех канвасов
                canvas_sizes = [(c.winfo_width(), c.winfo_height()) for c in self.monitor_canvases]
                
                # Делаем один большой скриншот всего виртуального экрана
                full_screenshot = pyautogui.screenshot()
                full_screenshot = np.array(full_screenshot)
                
                # Разделяем на отдельные мониторы
                screen_width = pyautogui.size()[0]
                for i, (canvas_w, canvas_h) in enumerate(canvas_sizes):
                    if canvas_w > 0 and canvas_h > 0:
                        # Вырезаем область текущего монитора
                        monitor_img = full_screenshot[:, i*screen_width:(i+1)*screen_width]
                        
                        # Масштабируем под размер канваса
                        scale = min(canvas_w / monitor_img.shape[1], 
                                  canvas_h / monitor_img.shape[0])
                        new_width = int(monitor_img.shape[1] * scale)
                        new_height = int(monitor_img.shape[0] * scale)
                        
                        if new_width > 0 and new_height > 0:
                            resized = cv2.resize(monitor_img, (new_width, new_height))
                            self.monitor_images = getattr(self, 'monitor_images', [])
                            if len(self.monitor_images) <= i:
                                self.monitor_images.append(None)
                            self.monitor_images[i] = ImageTk.PhotoImage(
                                image=Image.fromarray(resized))
                            self.monitor_canvases[i].create_image(
                                canvas_w//2, canvas_h//2, 
                                image=self.monitor_images[i], anchor=tk.CENTER)
            
            except Exception as e:
                print(f"Ошибка при обновлении экранов: {e}")
            
            time.sleep(self.update_delay / 1000)
    
    def capture_all_screens(self):
        """Сохраняет скриншоты всех мониторов"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        full_screenshot = pyautogui.screenshot()
        screen_width = pyautogui.size()[0]
        
        for i in range(self.num_monitors):
            try:
                filename = f"screen_monitor_{i+1}_{timestamp}.png"
                # Вырезаем область текущего монитора
                monitor_img = full_screenshot.crop((
                    i * screen_width, 0,
                    (i + 1) * screen_width, full_screenshot.height
                ))
                monitor_img.save(filename)
                print(f"Снимок монитора {i+1} сохранен как {filename}")
            except Exception as e:
                print(f"Ошибка при сохранении монитора {i+1}: {e}")
    
    def capture_single_screen(self, monitor_idx):
        """Сохраняет скриншот конкретного монитора"""
        if 0 <= monitor_idx < self.num_monitors:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screen_monitor_{monitor_idx+1}_{timestamp}.png"
            try:
                screen_width = pyautogui.size()[0]
                full_screenshot = pyautogui.screenshot()
                monitor_img = full_screenshot.crop((
                    monitor_idx * screen_width, 0,
                    (monitor_idx + 1) * screen_width, full_screenshot.height
                ))
                monitor_img.save(filename)
                print(f"Снимок монитора {monitor_idx+1} сохранен как {filename}")
            except Exception as e:
                print(f"Ошибка при сохранении монитора {monitor_idx+1}: {e}")
    
    def close(self):
        """Закрываем приложение"""
        self.running = False
        self.window.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = MultiMonitorApp(root, "Демонстрация нескольких мониторов")
    except ValueError as e:
        print(e)
        root.destroy()