import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import random
import string
from PIL import Image, ImageTk
from datetime import datetime
from plyer import notification

class TempMailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickMailX")
        self.root.geometry("500x650")
        self.root.resizable(False, False)  # Убираем возможность изменения размера окна

        self.light_bg = "#E0E5EC"
        self.dark_bg = "#2E2E2E"
        self.light_fg = "#000000"
        self.dark_fg = "#FFFFFF"
        self.current_theme = "light"

        # Настройка стилей для кнопок
        self.style = ttk.Style()
        self.style.configure("TButtonLight.TButton", background=self.light_bg, foreground=self.light_fg, relief="flat")
        self.style.map("TButtonLight.TButton", background=[('active', self.light_bg), ('!disabled', self.light_bg)], foreground=[('active', self.light_fg), ('!disabled', self.light_fg)])

        self.style.configure("TButtonDark.TButton", background=self.dark_bg, foreground=self.dark_fg, relief="flat")
        self.style.map("TButtonDark.TButton", background=[('active', self.dark_bg), ('!disabled', self.dark_bg)], foreground=[('active', self.dark_fg), ('!disabled', self.dark_fg)])

        self.set_background()

        # Метка для почты
        self.email_label = ttk.Label(root, text="Временная почта:", font=("Roboto", 12), background=self.light_bg)
        self.email_label.pack(pady=5)

        # Верхняя рамка для метки почты и кнопок
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(pady=5)

        # Рамка для кнопок "Сгенерировать почту" и "Проверить почту"
        self.buttons_frame = ttk.Frame(self.top_frame)
        self.buttons_frame.pack(pady=0)

        self.generate_icon = ImageTk.PhotoImage(file="image/generate.png")
        self.check_icon = ImageTk.PhotoImage(file="image/check.png")

        self.generate_button = ttk.Button(self.buttons_frame, text="Сгенерировать почту", image=self.generate_icon, compound="left", command=self.generate_email, style="TButtonLight.TButton")
        self.generate_button.pack(side="left", padx=[0, 15], pady=0)

        self.check_mail_button = ttk.Button(self.buttons_frame, text="Проверить почту", image=self.check_icon, compound="left", command=self.check_email, style="TButtonLight.TButton")
        self.check_mail_button.pack(side="left", padx=[15, 0], pady=0)

        # Рамка для ввода почты и кнопки копирования
        self.email_frame = ttk.Frame(root)
        self.email_frame.pack(pady=5)

        self.domain_var = tk.StringVar(value="1secmail.com")
        self.domain_entry = ttk.Combobox(self.email_frame, textvariable=self.domain_var, values=["1secmail.com", "mailinator.com", "10minutemail.com"], state="readonly")
        self.domain_entry.pack(side="left", padx=5)

        self.email_entry = tk.Entry(self.email_frame, width=30, font=("Roboto", 12))
        self.email_entry.pack(side="left")

        self.copy_icon = ImageTk.PhotoImage(file="image/copy.png")
        self.copy_button = ttk.Button(self.email_frame, image=self.copy_icon, command=self.copy_email, style="TButtonLight.TButton")
        self.copy_button.pack(side="left", padx=5)

        # Текстовое поле для отображения сообщений
        self.messages_frame = ttk.Frame(root)
        self.messages_frame.pack(pady=5)

        self.messages_text = tk.Text(self.messages_frame, height=20, width=50, font=("Roboto", 12), bd=0, relief="flat")
        self.messages_text.pack(side="left")

        self.scrollbar = tk.Scrollbar(self.messages_frame, command=self.messages_text.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.messages_text.config(yscrollcommand=self.scrollbar.set)

        # Переключатель темной темы
        self.theme_switch_frame = ttk.Frame(root)
        self.theme_switch_frame.pack(pady=5)

        self.sun_icon = ImageTk.PhotoImage(file="image/sun.png")
        self.moon_icon = ImageTk.PhotoImage(file="image/moon.png")
        self.clear_icon = ImageTk.PhotoImage(file="image/clear.png")
        self.settings_icon = ImageTk.PhotoImage(file="image/settings.png")

        self.theme_button = ttk.Button(self.theme_switch_frame, image=self.sun_icon, command=self.toggle_theme, style="TButtonLight.TButton")
        self.theme_button.pack(side="left", padx=(0, 5))

        self.settings_button = ttk.Button(self.theme_switch_frame, image=self.settings_icon, command=self.open_settings, style="TButtonLight.TButton")
        self.settings_button.pack(side="left", padx=(0, 5))

        self.clear_history_button = ttk.Button(self.theme_switch_frame, image=self.clear_icon, command=self.clear_history, style="TButtonLight.TButton")
        self.clear_history_button.pack(side="left", padx=(0, 5))

        # История сгенерированных почтовых адресов
        self.history_label = ttk.Label(root, text="История почты:", font=("Roboto", 12), background=self.light_bg)
        self.history_label.pack(pady=5)

        self.history_listbox = tk.Listbox(root, height=5, width=50, font=("Roboto", 12), bd=0, relief="flat")
        self.history_listbox.pack(pady=5)

        # Лоадер
        self.loader = None
        self.loader_canvas = tk.Canvas(root, width=50, height=50, bg=self.light_bg, highlightthickness=0)
        self.loader_canvas.pack(pady=5)
        self.draw_loader()

        self.email = ""
        self.history = []

        # Автообновление
        self.update_interval = 30000  # 30 секунд
        self.update_email_check()

    def set_background(self):
        if self.current_theme == "light":
            bg_image = Image.open("image/fon.jpg")
        else:
            bg_image = Image.open("image/dfon.jpg")

        bg_image = bg_image.resize((500, 650), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)
        if hasattr(self, 'bg_label'):
            self.bg_label.configure(image=self.bg_image)
        else:
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()

    def generate_email(self):
        domain = self.domain_var.get()
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email = f"{name}@{domain}"
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, self.email)
        self.messages_text.delete(1.0, tk.END)

        self.history.append(self.email)  # Добавляем email в историю
        self.history_listbox.insert(tk.END, f"{self.email} - {self.get_current_time()}")  # Обновляем список истории

    def copy_email(self):
        email = self.email_entry.get()
        if email:
            self.root.clipboard_clear()
            self.root.clipboard_append(email)
            self.root.update()  # Необходимо для некоторых ОС
            messagebox.showinfo("Копировать", "Email успешно скопирован в буфер обмена")
        else:
            messagebox.showwarning("Копировать", "Поле email пустое")

    def check_email(self):
        email = self.email_entry.get()
        if not email:
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(tk.END, "Сначала сгенерируйте почту")
            return

        self.show_loader()
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.insert(tk.END, "Проверка почты, пожалуйста подождите...")
        self.root.update()

        user, domain = email.split('@')
        try:
            response = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}")
            if response.status_code == 200:
                messages = response.json()
                self.messages_text.delete(1.0, tk.END)
                if not messages:
                    self.messages_text.insert(tk.END, "Нет новых сообщений")
                else:
                    for message in messages:
                        message_id = message['id']
                        from_address = message['from']
                        subject = message['subject']
                        date = message['date']
                        self.messages_text.insert(tk.END, f"От: {from_address}\nТема: {subject}\nДата: {date}\n\n")
                        self.root.update()
            else:
                self.messages_text.delete(1.0, tk.END)
                self.messages_text.insert(tk.END, f"Ошибка: {response.status_code}")
        except Exception as e:
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(tk.END, f"Ошибка: {str(e)}")
        finally:
            self.hide_loader()
            self.root.update()

    def draw_loader(self):
        self.loader_canvas.delete("all")
        self.loader_canvas.create_oval(10, 10, 40, 40, outline="black", width=2)
        self.loader_canvas.create_arc(10, 10, 40, 40, start=0, extent=90, outline="black", width=2, style="arc")
        self.loader_canvas.create_arc(10, 10, 40, 40, start=90, extent=180, outline="black", width=2, style="arc")
        self.loader_canvas.create_arc(10, 10, 40, 40, start=180, extent=270, outline="black", width=2, style="arc")

    def show_loader(self):
        self.loader_canvas.pack()

    def hide_loader(self):
        self.loader_canvas.pack_forget()

    def update_email_check(self):
        self.check_email()
        self.root.after(self.update_interval, self.update_email_check)

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.theme_button.configure(image=self.moon_icon, style="TButtonDark.TButton")
        else:
            self.current_theme = "light"
            self.theme_button.configure(image=self.sun_icon, style="TButtonLight.TButton")

        self.set_background()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("500x500")

        # Интервал обновления
        interval_label = ttk.Label(settings_window, text="Интервал обновления (мс):", font=("Roboto", 12))
        interval_label.pack(pady=5)

        self.interval_var = tk.StringVar(value=str(self.update_interval))
        interval_entry = ttk.Entry(settings_window, textvariable=self.interval_var)
        interval_entry.pack(pady=5)

        save_button = ttk.Button(settings_window, text="Сохранить", command=self.save_settings)
        save_button.pack(pady=10)

        # Кнопка смены обоев
        wallpaper_button = ttk.Button(settings_window, text="Сменить обои", command=self.change_wallpaper)
        wallpaper_button.pack(pady=10)

        # Описание продукта и версия
        version_label = ttk.Label(settings_window, text="Версия 1.2.26\nОписание продукта", font=("Roboto", 12))
        version_label.pack(pady=10)

    def save_settings(self):
        try:
            interval = int(self.interval_var.get())
            if interval > 0:
                self.update_interval = interval
                messagebox.showinfo("Настройки", "Настройки сохранены")
            else:
                messagebox.showwarning("Настройки", "Интервал должен быть положительным числом")
        except ValueError:
            messagebox.showwarning("Настройки", "Введите корректное значение интервала")

    def change_wallpaper(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.bg_image = Image.open(filepath).resize((500, 650), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
            self.bg_label.configure(image=self.bg_image)

    def clear_history(self):
        self.history = []
        self.history_listbox.delete(0, tk.END)

    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def notify(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = TempMailApp(root)
    root.mainloop()
