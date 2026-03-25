import tkinter as tk
from tkinter import messagebox, ttk
from user import Customer
import database as db


class CustomerFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg="light grey")
        self.root = root

        # ── Left panel 
        left_frame = tk.Frame(self, padx=10, pady=10, bg="light grey")
        left_frame.grid(row=0, column=0, sticky="ns")

        # Right panel
        right_frame = tk.Frame(self, padx=10, pady=10, bg="light grey")
        right_frame.grid(row=0, column=1, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        tk.Button(left_frame, text="<<", command=self.go_back,
                  font=("Arial", 9, "bold"), width=7, height=2).grid(
            row=0, column=0, padx=10, pady=(50, 30))
        tk.Label(left_frame, text="Register a new customer below:",
                 bg="light grey", font=("Helvetica", 15, "bold")).grid(
            row=0, column=1, padx=10, pady=(50, 30))

        for row_i, text in enumerate(("ID Number:", "Name:", "Phone Number:"), start=1):
            tk.Label(left_frame, text=text, bg="light grey",
                     font=("", 11)).grid(row=row_i, column=0, padx=5, pady=10)

        self.entry_id_number = tk.Entry(left_frame, width=30, font=("", 11))
        self.entry_name      = tk.Entry(left_frame, state='disabled', width=30, font=("", 11))
        self.entry_phone     = tk.Entry(left_frame, state='disabled', width=30, font=("", 11))

        self.entry_id_number.grid(row=1, column=1, padx=10, pady=10)
        self.entry_name.grid(row=2, column=1, pady=10)
        self.entry_phone.grid(row=3, column=1, pady=10)
        self.entry_id_number.focus_set()

        tk.Label(left_frame, text=" ", bg="light grey").grid(row=4, column=1, padx=10, pady=10)

        self.entry_id_number.bind("<Return>", lambda e: self.entry_name.focus_set())
        self.entry_name.bind("<Return>",      lambda e: self.entry_phone.focus_set())
        self.entry_phone.bind("<Return>",     lambda e: self.save_customer())

        tk.Button(left_frame, text="Search", command=self.search_id,
                  bg="#BDBDBD", width=7, height=1,
                  font=("Arial", 11, "bold")).grid(row=1, column=2, pady=10)
        tk.Button(left_frame, text="Save", command=self.save_customer,
                  height=3, width=15, foreground="white",
                  bg="#3979B4", font=("Arial", 12)).grid(row=5, column=1, columnspan=2, pady=10)
        tk.Button(left_frame, text="Edit", command=self.edit_customer,
                  height=3, width=15, foreground="white",
                  bg="#3979B4", font=("Arial", 12)).grid(row=6, column=1, columnspan=2, pady=10)
        tk.Button(left_frame, text="Delete", command=self.delete_customer,
                  height=3, width=15, foreground="white",
                  bg="#3979B4", font=("Arial", 12)).grid(row=10, column=1, columnspan=2, pady=20)

        # ── Right panel 
        search_frame = tk.Frame(right_frame, padx=10, pady=10, bg="light grey")
        search_frame.grid(row=0, column=0, sticky="ew")

        tk.Label(search_frame, text="Search by ID:", bg="light grey",
                 font=("", 11)).pack(side=tk.LEFT, padx=10)
        self.search_entry = tk.Entry(search_frame, font=("", 11))
        self.search_entry.pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Search Customer",
                  command=self.search_customer, font=("", 11)).pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Show All",
                  command=self.load_customers, font=("", 11)).pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Show Customer Sales",
                  command=self.show_customer_sales, font=("", 11)).pack(side=tk.LEFT, padx=10)

        tree_frame = tk.Frame(right_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Phone"), show='headings')
        for col, text in [("ID", "ID Number"), ("Name", "Name"), ("Phone", "Phone Number")]:
            self.tree.heading(col, text=text)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        self.load_customers()

    def go_back(self):
        self.root.show_frame("Options")

    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in db.get_all_customers():
            self.tree.insert("", tk.END, values=(row["id_number"], row["name"], row["phone"]))

    def search_id(self):
        id_number = self.entry_id_number.get().strip()
        if not id_number:
            messagebox.showwarning("Input Error", "Please enter an ID number.")
            return
        if db.customer_exists(id_number):
            messagebox.showinfo("Info", "This ID has already been registered.")
            self.entry_name.config(state='disabled')
            self.entry_phone.config(state='disabled')
        else:
            self.entry_name.config(state='normal')
            self.entry_phone.config(state='normal')

    def save_customer(self):
        id_number = self.entry_id_number.get().strip()
        name      = self.entry_name.get().strip()
        phone     = self.entry_phone.get().strip()

        if not all([id_number, name, phone]):
            messagebox.showwarning("Input Error", "Please fill in all required fields.")
            return

        if not db.save_customer(id_number, name, phone):
            messagebox.showerror("Error", "A customer with this ID already exists.")
            return

        messagebox.showinfo("Success", "Customer saved successfully!")
        for entry in (self.entry_id_number, self.entry_name, self.entry_phone):
            entry.delete(0, tk.END)
        self.load_customers()

    def search_customer(self):
        search_id = self.search_entry.get().strip()
        if not search_id:
            messagebox.showwarning("Input Error", "Please enter an ID number.")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in db.search_customers_by_id(search_id):
            self.tree.insert("", tk.END, values=(row["id_number"], row["name"], row["phone"]))

    def edit_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a customer to edit.")
            return

        values = self.tree.item(selected[0], "values")

        win = tk.Toplevel()
        win.title("Edit Customer")
        win.geometry("600x400")
        win.iconbitmap("../assets/show_customer.ico")
        win.resizable(False, False)

        frame = tk.Frame(win, padx=60, pady=10, bg="light grey")
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        tk.Label(frame, text=f"Edit the data for {values[1]}",
                 font=('Helvetica', 16, 'bold'), bg="light grey").pack(pady=20)

        field_frame = tk.Frame(frame, bg="light grey", padx=50)
        field_frame.pack(expand=True, fill=tk.BOTH, pady=5, padx=30)

        labels = ("ID Number:", "Name:", "Phone Number:")
        entries = []
        for i, (lbl, val) in enumerate(zip(labels, values)):
            tk.Label(field_frame, text=lbl, bg="light grey").grid(row=i, column=0, pady=10, sticky='e')
            e = tk.Entry(field_frame)
            e.grid(row=i, column=1, pady=10, padx=10, sticky='w')
            e.insert(0, val)
            entries.append(e)

        def save_changes():
            new_id, new_name, new_phone = [e.get().strip() for e in entries]
            db.update_customer(values[0], new_id, new_name, new_phone)
            messagebox.showinfo("Success", "Customer updated successfully!")
            self.load_customers()
            win.destroy()

        tk.Button(frame, text="Save Changes", command=save_changes,
                  height=2, width=15, bd=2, font=("Arial", 10),
                  foreground="white", bg="#3979B4").pack(pady=10)

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a customer to delete.")
            return
        values = self.tree.item(selected[0], "values")
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this customer?"):
            db.delete_customer(values[0])
            self.tree.delete(selected[0])
            messagebox.showinfo("Success", "Customer deleted successfully!")

    def show_customer_sales(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a customer.")
            return
        values = self.tree.item(selected[0], "values")
        customer_id, customer_name = values[0], values[1]

        win = tk.Toplevel()
        win.title("Customer Sales")
        win.geometry("800x500")
        win.iconbitmap("../assets/show_customer.ico")

        frame = tk.Frame(win, padx=10, pady=10, bg="light grey")
        frame.pack(expand=True, fill=tk.BOTH)
        tk.Label(frame, text=f"{customer_name} purchases",
                 bg="light grey", font=("Helvetica", 12, "bold")).pack(pady=40)

        tree_frame = tk.Frame(frame)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        cols = ("Receipt", "Date", "Customer ID", "Customer Name", "Description", "Total")
        widths = (45, 95, 55, 90, 320, 40)
        sales_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col, w in zip(cols, widths):
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=w)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=sales_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=sales_tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        sales_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        sales_tree.pack(expand=True, fill=tk.BOTH)

        for row in db.get_sales_by_customer(customer_id):
            sales_tree.insert("", tk.END, values=(
                row["receipt_no"], row["date"], row["customer_id"],
                row["customer_name"], row["description"], row["total"]
            ))


def create_customer_frame(parent, root):
    frame = CustomerFrame(parent, root)
    frame.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return frame
