import tkinter as tk
import customtkinter as ctk
import time
import sqlite3 as sql
from tkinter import ttk
from PIL import ImageTk, Image  
from pathlib import Path
from ctypes import windll

#https://stackoverflow.com/questions/66626254/tkinter-cant-open-image
#https://customtkinter.tomschimansky.com/documentation/packaging
#https://stackoverflow.com/questions/4066027/making-tkinter-windows-show-up-in-the-taskbar
##fixed the disappearing icon 
#https://www.youtube.com/watch?v=Gnk9DdKqbnQ 

class TestConst:
    def __init__(self, x, y):
        self.name = x
        self.pic = y

class Library_UI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_working_directory = Path(__file__).parent.absolute()
        self.image_directory = f"{self.current_working_directory}\\assets\\student_images\\"
        self.assets_directory = f"{self.current_working_directory}\\assets\\"
        self.iconpath = ImageTk.PhotoImage(file=f"{self.image_directory}STI.png")
        self.wm_iconbitmap()
        self.wm_iconphoto(False, self.iconpath)

        self.overrideredirect(True)

        self.title("STI Library Login")
        self.geometry("500x500")

        self.custom_titlebar()
        self.main()
        self.update_time()
        self.event_binds()

        self.login = False
        self.id = ""

    def overrideredirect(self, boolean):
        ctk.CTk.overrideredirect(self, boolean)
        GWL_EXSTYLE=-20
        WS_EX_APPWINDOW=0x00040000
        WS_EX_TOOLWINDOW=0x00000080
        if boolean:
            hwnd = windll.user32.GetParent(self.winfo_id())
            style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        self.wm_withdraw()
        self.wm_deiconify()

    def center_frame(self, root, frame):
        frame.pack(expand=True, fill='both')
        self.update_idletasks()  # Update the window to get its actual size
        frame.place(in_=self, anchor="c", relx=0.5, rely=0.5)

    def custom_titlebar(self):
        self.title_bar = ctk.CTkFrame(self)
        self.title_bar.pack(side="top", fill="x")
        icon_image = ctk.CTkImage(Image.open(f"{self.image_directory}STI.png"), size=(25, 25))
        title_icon = ctk.CTkLabel(self.title_bar, text="", image=icon_image, )
        title_icon.pack(side="left", padx=8, pady=1)
        title_label = ctk.CTkLabel(self.title_bar, text="STI Library Login")
        title_label.pack(side="left")
        self.exit_button = ctk.CTkButton(self.title_bar, text=" X ", width=50)
        self.exit_button.pack(side="right")
        self.button_enabled = tk.BooleanVar()
        self.button_enabled.set(False)

    def main(self):
        self.main_screen = ctk.CTkFrame(self)
        self.center_frame(self, self.main_screen)
        user_picture = ctk.CTkImage(Image.open(f"{self.image_directory}blank.png"), size=(120, 120))
        self.picture_label = ctk.CTkLabel(self.main_screen, text="", image=user_picture)
        self.picture_label.pack(padx=30, pady=15)
        self.user_name = ctk.CTkLabel(self.main_screen, text="- - -")
        self.user_name.pack()
        self.search_bar = ctk.CTkEntry(self.main_screen)
        self.search_bar.pack()
        self.test_text = ctk.CTkLabel(self.main_screen, height=29)
        self.test_text.pack()

    def event_binds(self):
        self.search_bar.bind("<Return>", lambda event: Events.login(self, event))
        self.title_bar.bind("<ButtonPress-1>", lambda event: Events.on_drag_start(self, event))
        self.title_bar.bind("<ButtonRelease-1>", lambda event: Events.on_drag_stop(self, event))
        self.title_bar.bind("<B1-Motion>", lambda event: Events.on_drag(self, event))
        self.exit_button.bind("<ButtonRelease-1>", lambda event: Events.on_button_click(self, event))
        self.exit_button.bind("<Enter>", lambda event: Events.on_mouse_enter(self, event))
        self.exit_button.bind("<Leave>", lambda event: Events.on_mouse_leave(self, event)) 

    def update_time(self):
        current_time = time.strftime('%I:%M:%S %p')
        self.test_text.configure(text=f"The time is {current_time}")
        self.after(1000, self.update_time)

class Events(Library_UI):
    def login(self, event):
        try:
            if self.login:
                self.after_cancel(self.id)

            user = Events.data_fetch(self)
        
            user_picture = ctk.CTkImage(Image.open(f"{self.image_directory}\\{user[3]}"), size=(120, 120))
            self.picture_label.configure(text="", image=user_picture)
            self.user_name.configure(text=user[1])
            self.search_bar.delete(0, tk.END)
            self.login = True
            self.id = self.after(3000, lambda: Events.test(self))
        except FileNotFoundError:
            #error when cannot find user
            self.search_bar.delete(0, tk.END)
        except TypeError: 
            #error when input involves characters
            self.search_bar.delete(0, tk.END)

    def data_fetch(self):
        db = sql.connect(f"file:{self.assets_directory}informations.sqlite?mode=rw", uri=True)
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM Users WHERE TagID = "{self.search_bar.get()}"')

        user = cursor.fetchone()

        cursor.close()
        db.close()

        return user

    def test(self):
        self.picture_label.configure(text="", image=ctk.CTkImage(Image.open(f"{self.image_directory}blank.png"), size=(120, 120)))
        self.user_name.configure(text="- - -")
        self.login = False
    
    def on_drag_start(self, event):
        self.start_x = event.x_root - self.winfo_x()
        self.start_y = event.y_root - self.winfo_y()
    
    def on_drag_stop(self, event):
        self.start_x = None
        self.start_y = None
    
    def on_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            x = event.x_root - self.start_x
            y = event.y_root - self.start_y
            self.geometry(f"+{x}+{y}")

    def on_button_click(self, event):
        if self.button_enabled.get():
            self.destroy()

    def on_mouse_enter(self, event):
        self.button_enabled.set(True)

    def on_mouse_leave(self, event):
        self.button_enabled.set(False)

if __name__ == "__main__":
    Library_UI().mainloop()