import tkinter as tk


class OptionsFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg="#A5B4C2")
        self.root = root

        # Title bar
        title_frame = tk.Frame(self, bg="white")
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=20)
        tk.Label(title_frame, text="Welcome! Select an option:",
                 font=("Helvetica", 20, "bold"), bg="white").pack(pady=(40, 20))

        # Buttons — centered with expand=True so they stay centred on any screen size
        buttons_frame = tk.Frame(self, bg="#A5B4C2")
        buttons_frame.pack(expand=True, pady=5)

        btn_cfg = dict(width=30, height=4, font=("Segoe UI", 16), bd=3)
        tk.Button(buttons_frame, text="SALES",
                  command=lambda: root.show_frame("Sales"), **btn_cfg).pack(side=tk.LEFT, padx=30)
        tk.Button(buttons_frame, text="INVENTORY",
                  command=lambda: root.show_frame("Inventory"), **btn_cfg).pack(side=tk.LEFT, padx=30)
        tk.Button(buttons_frame, text="CUSTOMER",
                  command=lambda: root.show_frame("Customer"), **btn_cfg).pack(side=tk.LEFT, padx=30)


def create_options_frame(parent, root):
    frame = OptionsFrame(parent, root)
    frame.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return frame
