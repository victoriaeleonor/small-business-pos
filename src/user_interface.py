import tkinter as tk
from tkinter import messagebox
from user import User
from login_frame import create_login_frame
from options_frame import create_options_frame
from sales_frame import create_sales_frame
from inventory_frame import create_inventory_frame
from customer_frame import create_customer_frame
import database as db


class UserInterface:    # Base class
    def __init__(self, root):
        self.root = root
        self.root.title("Canteen")
        self.root.configure(bg="grey")
        self.root.state('zoomed')

        self.frames = {}
        self.create_frames()
        self.create_menu_bar()
        self.show_frame("Login")

    def create_frames(self):
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames["Login"]     = create_login_frame(container, self, self.root)
        self.frames["Options"]   = create_options_frame(container, self)
        self.frames["Sales"]     = create_sales_frame(container, self)
        self.frames["Inventory"] = create_inventory_frame(container, self)
        self.frames["Customer"]  = create_customer_frame(container, self)

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self.root)
        self.menu_bar.add_command(label="    Log Out     ", command=self.logout)
        self.menu_bar.add_command(label="    Register    ", command=self.register_window)

    def logout(self):
        self.root.config(menu="")
        self.show_frame("Login")
        messagebox.showinfo("Logged Out", "Session successfully closed.")

    def register_window(self):
        win = tk.Toplevel()
        win.title("Register")
        win.geometry("600x500")
        win.iconbitmap("../assets/new_register.ico")

        frame = tk.Frame(win, padx=50, pady=20, bg="light grey")
        frame.pack(expand=True)

        tk.Label(frame, text="REGISTER A NEW USER", font=("Helvetica", 16),
                 bg="light grey").pack(side=tk.TOP, pady=20)

        fields = {}
        for label in ("Name", "Username"):
            tk.Label(frame, text=f"{label}:", bg="light grey").pack(padx=10, pady=10)
            e = tk.Entry(frame, bg="#F4F4F4")
            e.pack(padx=10, pady=5)
            fields[label] = e

        tk.Label(frame, text="Password:", bg="light grey").pack(padx=10, pady=10)
        entry_password = tk.Entry(frame, show="*", bg="#F4F4F4")
        entry_password.pack(padx=10, pady=5)

        tk.Label(frame, text="Confirm Password:", bg="light grey").pack(padx=10, pady=10)
        entry_confirm = tk.Entry(frame, show="*", bg="#F4F4F4")
        entry_confirm.pack(padx=10, pady=5)

        fields["Name"].focus_set()
        fields["Name"].bind("<Return>",     lambda e: fields["Username"].focus_set())
        fields["Username"].bind("<Return>", lambda e: entry_password.focus_set())
        entry_password.bind("<Return>",     lambda e: entry_confirm.focus_set())

        def register():
            name     = fields["Name"].get().strip()
            username = fields["Username"].get().strip()
            password = entry_password.get()
            confirm  = entry_confirm.get()

            if not all([name, username, password, confirm]):
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            if not db.save_user(name, username, password):
                messagebox.showerror("Error", f"Username '{username}' is already taken.")
                return

            win.destroy()
            messagebox.showinfo("Success", f"User '{username}' registered successfully.")

        entry_confirm.bind("<Return>", lambda e: register())
        tk.Button(frame, text="Register", command=register,
                  width=7, height=2, bd=2, bg="#3979B4",
                  font=("Arial", 12, "bold"), foreground="white").pack(pady=20)

    def show_frame(self, frame_name):
        self.frames[frame_name].tkraise()
