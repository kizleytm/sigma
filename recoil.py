import customtkinter as ctk
import keyboard
import ctypes
import os
import configparser
import ast
import threading
import time
from tkinter import messagebox

# Global variables
aim_check = False
x_value = 0
y_value = 0
left_value = 0
delay_value = 10
enabled = False
current_loadout_name = None

# Check for config file
config_folder = "Config"
if not os.path.exists(config_folder):
    os.makedirs(config_folder)

config_path = os.path.join(config_folder, "config.txt")
if not os.path.isfile(config_path):
    print("config.txt file not found. Creating new one...")
    config = configparser.ConfigParser()
    config["hotkey"] = {"hotkey_on": "f1", "hotkey_off": "f2"}
    config["loadouts"] = {}
    with open(config_path, "w") as configfile:
        config.write(configfile)
    input("Press any key to exit...")
    exit()
else:
    config = configparser.ConfigParser()
    config.read(config_path)

# Main application class
class RecoilMacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clavish.cc Recoil")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Frame setup
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.sidebar_label = ctk.CTkLabel(
            self.sidebar_frame, text="Loadouts", font=("Arial", 18, "bold"), text_color="white"
        )
        self.sidebar_label.pack(pady=10)

        self.loadout_buttons = ctk.CTkScrollableFrame(self.sidebar_frame, height=400)
        self.loadout_buttons.pack(fill="both", expand=True, pady=10)

        self.refresh_loadout_buttons()

        # Button frame
        self.button_frame = ctk.CTkFrame(self.sidebar_frame)
        self.button_frame.pack(pady=10)

        self.loadout_name_entry = ctk.CTkEntry(self.button_frame, width=150)
        self.loadout_name_entry.grid(row=0, column=0, padx=5)

        self.add_loadout_button = ctk.CTkButton(
            self.button_frame,
            text="Add New Loadout",
            command=self.save_loadout,
            fg_color="#0000ff",  # Set button color to blue
            hover_color="#0000ff",  # Set hover color to blue
            width=150,
        )
        self.add_loadout_button.grid(row=0, column=1, padx=5)

        # Content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Clavish.cc Recoil",
            font=("Arial", 24, "bold"),
            text_color="white",
        )
        self.title_label.pack(pady=20)

        self.recoil_status_label = ctk.CTkLabel(
            self.content_frame, text="Recoil Off🔴", text_color="#FF0000", font=("Arial", 16)
        )
        self.recoil_status_label.pack(side="top", anchor="ne", padx=10, pady=10)

        # Sliders
        self.x_label = ctk.CTkLabel(self.content_frame, text="X Control Value (Right)", text_color="white")
        self.x_label.pack(pady=5)
        self.x_slider = ctk.CTkSlider(
            self.content_frame,
            from_=0,
            to=40,
            number_of_steps=40,
            command=self.on_slider_change,
            button_color="#0000ff",
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
            button_color="#0000ff",
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
            button_color="#0000ff",
        )
        self.y_slider.pack(pady=5)
        self.y_value_label = ctk.CTkLabel(self.content_frame, text="Y Value: 20", text_color="white")
        self.y_value_label.pack(pady=5)

        # Hotkey for enabling and disabling macro
        keyboard.add_hotkey("f1", self.enable_macro)
        keyboard.add_hotkey("f2", self.disable_macro)

        # Start the macro thread
        self.macro_thread = threading.Thread(target=self.macro_task)
        self.macro_thread.daemon = True
        self.macro_thread.start()

        # Help button
        self.help_button = ctk.CTkButton(
            self.content_frame,
            text="Help",
            command=self.show_help,
            fg_color="#0000ff",  # Set button color to blue
            hover_color="#0000ff",  # Set hover color to blue
            width=150,
        )
        self.help_button.pack(pady=20)

    def refresh_loadout_buttons(self):
        for widget in self.loadout_buttons.winfo_children():
            widget.destroy()

        for name in config["loadouts"]:
            button = ctk.CTkButton(
                self.loadout_buttons,
                text=name,
                command=self.create_loadout_callback(name),
                fg_color="#0000ff",  # Set button color to blue
                hover_color="#0000ff",  # Set hover color to blue
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
            with open(config_path, "w") as configfile:
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
        # Check which slider was changed and update the corresponding value
        if value == self.x_slider.get():
            x_value = int(value)
            self.update_x_value(x_value)
        elif value == self.left_slider.get():
            left_value = int(value)
            self.update_left_value(left_value)
        elif value == self.y_slider.get():
            y_value = int(value)
            self.update_y_value(y_value)

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

    def show_help(self):
        help_text = """
        Clavish.cc Recoil - User Guide:
        - Use sliders to adjust recoil values.
        - Press F1 to enable the macro and F2 to disable it.
        - Save and load different recoil loadouts for quick access.
        """
        messagebox.showinfo("Help", help_text)


if __name__ == "__main__":
    app = RecoilMacroApp()
    app.mainloop()
