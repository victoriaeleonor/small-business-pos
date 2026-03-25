import tkinter as tk
from tkinter import messagebox
import database as db


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller, root):
        super().__init__(parent, bg="#A5B4C2")
        self.controller = controller
        self.root = root

        # Central frame
        frame = tk.Frame(self, padx=80, pady=50, bg="white", bd=2, relief="flat")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="CANTEEN SYSTEM", bg="white",
                 font=("Helvetica", 22, "bold")).grid(row=0, column=0, padx=10, sticky="nsew")
        tk.Label(frame, text="Log In", bg="white",
                 font=("Courier", 17)).grid(row=1, column=0, padx=10, pady=20, sticky="w")
        tk.Label(frame, text=" ", bg="white").grid(row=2, column=0, pady=1)

        tk.Label(frame, text="Username:", font=("Arial", 12),
                 bg="white").grid(row=3, column=0, padx=10, sticky="w")
        tk.Label(frame, text="Password:", font=("Arial", 12),
                 bg="white").grid(row=5, column=0, padx=10, sticky="w")

        self.entry_user = tk.Entry(frame, bg="#F4F4F4", width=30, font=("Arial", 12))
        self.entry_password = tk.Entry(frame, show="*", bg="#F4F4F4", width=30, font=("Arial", 12))
        self.entry_user.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.entry_password.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.entry_user.focus_set()
        self.entry_user.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self.login())

        btn_login = tk.Button(frame, text="Log In", command=self.login,
                              width=2, height=2, bd=2, bg="#0979B0",
                              font=("Arial", 12, "bold"), foreground="black")
        btn_login.grid(row=7, column=0, pady=20, padx=10, sticky="nsew")

    def get_credentials(self):
        return self.entry_user.get(), self.entry_password.get()

    def clear_entries(self):
        self.entry_user.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def login(self):
        username, password = self.get_credentials()
        if db.verify_user(username, password):
            self.root.config(menu=self.controller.menu_bar)
            self.controller.show_frame("Options")
        else:
            messagebox.showerror(title="Error", message="Incorrect username or password")
        self.clear_entries()


def create_login_frame(parent, controller, root):
    frame = LoginFrame(parent, controller, root)
    frame.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return frame
