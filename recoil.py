import customtkinter as ctk
import keyboard
import ctypes
import os
import configparser
import ast
import threading
import time
from tkinter import Menu

aim_check = False
x_value = 0
y_value = 0
left_value = 0
delay_value = 10
enabled = False
current_loadout_name = None

if not os.path.isfile("config.txt"):
    print("config.txt file not found. Creating new one...")
    config = configparser.ConfigParser()
    config["hotkey"] = {"hotkey_on": "f1", "hotkey_off": "f2"}
    config["loadouts"] = {}
    with open("config.txt", "w") as configfile:
        config.write(configfile)
    input("Press any key to exit...")
    exit()
else:
    config = configparser.ConfigParser()
    config.read("config.txt")

class RecoilMacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Noxar Recoil")
        self.geometry("800x600")

        icon_path = os.path.join(os.getcwd(), "spotify_icon.ico")
        if os.path.isfile(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Failed to load icon: {e}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.aim_check = False
        self.save_message_label = None

        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.sidebar_label = ctk.CTkLabel(
            self.sidebar_frame, text="Loadouts", font=("Arial", 18, "bold"), text_color="white"
        )
        self.sidebar_label.pack(pady=10)

        self.loadout_buttons = ctk.CTkScrollableFrame(self.sidebar_frame, height=400)
        self.loadout_buttons.pack(fill="both", expand=True, pady=10)

        self.refresh_loadout_buttons()

        self.button_frame = ctk.CTkFrame(self.sidebar_frame)
        self.button_frame.pack(pady=10)

        self.loadout_name_entry = ctk.CTkEntry(self.button_frame, width=150)
        self.loadout_name_entry.grid(row=0, column=0, padx=5)

        self.add_loadout_button = ctk.CTkButton(
            self.button_frame,
            text="Add New Loadout",
            command=self.save_loadout,
            fg_color="#ff1493",
            hover_color="#ff1493",
            width=150,
        )
        self.add_loadout_button.grid(row=0, column=1, padx=5)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Noxar Recoil",
            font=("Arial", 24, "bold"),
            text_color="white",
        )
        self.title_label.pack(pady=20)

        self.recoil_status_label = ctk.CTkLabel(
            self.content_frame, text="Recoil Off🔴", text_color="#FF0000", font=("Arial", 16)
        )
        self.recoil_status_label.pack(side="top", anchor="ne", padx=10, pady=10)

        self.x_label = ctk.CTkLabel(self.content_frame, text="X Control Value (Right)", text_color="white")
        self.x_label.pack(pady=5)
        self.x_slider = ctk.CTkSlider(
            self.content_frame,
            from_=0,
            to=40,
            number_of_steps=40,
            command=self.on_slider_change,
            button_color="#ff1493",
        )
        self.x_slider.pack(pady=5)
        self.x_value_label = ctk.CTkLabel(self.content_frame, text="X Value: 20", text_color="white")
        self.x_value_label.pack(pady=5)

        self.left_label = ctk.CTkLabel(self.content_frame, text="Left Control Value (Left)", text_color="white")
        self.left_label.pack(pady=5)
        self.left_slider = ctk.CTkSlider(
            self.content_frame,
            from_=-40,
            to=0,
            number_of_steps=40,
            command=self.on_slider_change,
            button_color="#ff1493",
        )
        self.left_slider.pack(pady=5)
        self.left_value_label = ctk.CTkLabel(self.content_frame, text="Left Value: 20", text_color="white")
        self.left_value_label.pack(pady=5)

        self.y_label = ctk.CTkLabel(self.content_frame, text="Y Control Value (Down)", text_color="white")
        self.y_label.pack(pady=5)
        self.y_slider = ctk.CTkSlider(
            self.content_frame,
            from_=0,
            to=40,
            number_of_steps=40,
            command=self.on_slider_change,
            button_color="#ff1493",
        )
        self.y_slider.pack(pady=5)
        self.y_value_label = ctk.CTkLabel(self.content_frame, text="Y Value: 20", text_color="white")
        self.y_value_label.pack(pady=5)

        self.toggle_keys_label = ctk.CTkLabel(self.content_frame, text="Toggle: F1 On / F2 Off", text_color="white")
        self.toggle_keys_label.pack(pady=10)

        keyboard.add_hotkey("f1", self.enable_macro)
        keyboard.add_hotkey("f2", self.disable_macro)

        self.macro_thread = threading.Thread(target=self.macro_task)
        self.macro_thread.daemon = True
        self.macro_thread.start()

    def refresh_loadout_buttons(self):
        for widget in self.loadout_buttons.winfo_children():
            widget.destroy()

        for name in config["loadouts"]:
            button = ctk.CTkButton(
                self.loadout_buttons,
                text=name,
                command=self.create_loadout_callback(name),
                fg_color="#ff1493",
                hover_color="#ff1493",
            )
            button.pack(pady=5)

    def create_loadout_callback(self, name):
        return lambda: self.load_loadout(name)

    def load_loadout(self, name):
        global x_value, y_value, left_value, delay_value, current_loadout_name
        current_loadout_name = name
        loadout = ast.literal_eval(config["loadouts"][name])
        x_value, left_value, y_value, delay_value = loadout
        self.x_slider.set(x_value)
        self.left_slider.set(left_value)
        self.y_slider.set(y_value)
        self.update_x_value(x_value)
        self.update_left_value(left_value)
        self.update_y_value(y_value)

    def save_loadout(self):
        global x_value, y_value, left_value, delay_value
        name = self.loadout_name_entry.get() or f"Loadout {len(config['loadouts']) + 1}"
        config["loadouts"][name] = f"[{x_value},{left_value},{y_value},{delay_value}]"
        self.save_config_file()
        self.refresh_loadout_buttons()

    def save_config_file(self):
        try:
            with open("config.txt", "w") as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Save failed: {e}")

    def toggle_macro(self):
        global enabled
        enabled = not enabled
        self.update_toggle_state()

    def enable_macro(self):
        global enabled
        enabled = True
        self.update_toggle_state()

    def disable_macro(self):
        global enabled
        enabled = False
        self.update_toggle_state()

    def update_toggle_state(self):
        self.recoil_status_label.configure(
            text="Recoil On🟢" if enabled else "Recoil Off🔴",
            text_color="#00FF00" if enabled else "#FF0000",
        )

    def on_slider_change(self, value):
        global x_value, y_value, left_value
        x_value = int(self.x_slider.get())
        left_value = int(self.left_slider.get())
        y_value = int(self.y_slider.get())
        self.update_x_value(x_value)
        self.update_left_value(left_value)
        self.update_y_value(y_value)
        self.save_current_loadout()

    def save_current_loadout(self):
        global current_loadout_name, x_value, y_value, left_value, delay_value
        if current_loadout_name:
            config["loadouts"][current_loadout_name] = f"[{x_value},{left_value},{y_value},{delay_value}]"
            self.save_config_file()

    def macro_task(self):
        while True:
            if enabled:
                if (
                    ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000
                    and ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000
                ):
                    self.move_rel(x_value + left_value, y_value)
            time.sleep(delay_value / 1000)

    def move_rel(self, x, y):
        ctypes.windll.user32.mouse_event(0x0001, x, y, 0, 0)

    def update_x_value(self, value):
        self.x_value_label.configure(text=f"X Value: {int(float(value))}")

    def update_left_value(self, value):
        self.left_value_label.configure(text=f"Left Value: {int(float(value))}")

    def update_y_value(self, value):
        self.y_value_label.configure(text=f"Y Value: {int(float(value))}")

if __name__ == "__main__":
    app = RecoilMacroApp()
    app.mainloop()
