import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from openpyxl import Workbook
from datetime import datetime
import database as db


class InventoryFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg="light grey")
        self.root = root

        # ── Left: search + treeview ──────────────────────────────────────────
        left_frame = tk.Frame(self, bg="light grey")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20, expand=True)

        search_frame = tk.Frame(left_frame, bg="light grey")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(search_frame, text="INVENTORY", bg="light grey",
                 font=("Helvetica", 18, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        tk.Label(search_frame, text="Search by Name:", bg="light grey").grid(
            row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        tk.Button(search_frame, text="Search", command=self.search_product,
                  width=7, height=2).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Button(search_frame, text="Show All", command=self.show_all_products,
                  width=9, height=2).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Treeview
        tree_frame = tk.Frame(left_frame, bg="light grey")
        tree_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=("Product Code", "Product Name", "Quantity", "Unit Price"),
            show='headings'
        )
        for col, w in [("Product Code", 120), ("Product Name", 220),
                       ("Quantity", 90), ("Unit Price", 110)]:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=w)

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Right: action buttons ────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg="light grey")
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=30, pady=50)

        btn_cfg = dict(height=3, width=18, foreground="white",
                       bg="#3979B4", font=("Arial", 12))
        tk.Button(btn_frame, text="Add Product",
                  command=self.add_product, **btn_cfg).pack(pady=10, padx=30)
        tk.Button(btn_frame, text="Edit Product",
                  command=self.edit_product, **btn_cfg).pack(pady=10, padx=30)
        tk.Button(btn_frame, text="Delete Product",
                  command=self.delete_product, **btn_cfg).pack(pady=10, padx=30)
        tk.Button(btn_frame, text="Export to Excel",
                  command=self.export_to_excel,
                  height=3, width=18, foreground="black",
                  bg="white", font=("Arial", 12), bd=2).pack(pady=10, padx=30)
        tk.Button(btn_frame, text="<<", command=self.go_back,
                  height=2, width=8,
                  font=("Helvetica", 13, "bold")).pack(pady=20, padx=30)

        self.load_products()

    def go_back(self):
        self.root.show_frame("Options")

    def load_products(self):
        """Clears and reloads all products from the database."""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for row in db.get_all_products():
            self.inventory_tree.insert('', 'end',
                                       values=(row["product_code"], row["product_name"],
                                               row["quantity"], row["unit_price"]))

    def add_product(self):
        win = tk.Toplevel()
        win.title("Add Product")
        win.geometry("600x400")
        win.iconbitmap("../assets/add_product.ico")

        frame = tk.Frame(win, padx=70, pady=10, bg="light grey")
        frame.pack(expand=True)

        tk.Label(frame, text="ADD PRODUCT", font=("Helvetica", 16),
                 bg="light grey").pack(side=tk.TOP, pady=5)

        fields = {}
        for label in ("Product Code", "Product Name", "Quantity", "Unit Price"):
            tk.Label(frame, text=f"{label}:", bg="light grey").pack(padx=10, pady=10)
            entry = tk.Entry(frame, bg="#F4F4F4")
            entry.pack(padx=10, pady=5)
            fields[label] = entry

        entries = list(fields.values())
        entries[0].focus_set()
        for i in range(len(entries) - 1):
            entries[i].bind("<Return>", lambda e, nxt=entries[i + 1]: nxt.focus_set())

        def save():
            code = fields["Product Code"].get().strip()
            name = fields["Product Name"].get().strip()
            qty  = fields["Quantity"].get().strip()
            price = fields["Unit Price"].get().strip()
            if not all([code, name, qty, price]):
                messagebox.showwarning("Warning", "Please fill in all fields.")
                return
            try:
                qty, price = int(qty), float(price)
            except ValueError:
                messagebox.showerror("Error", "Quantity must be an integer and Unit Price a number.")
                return
            if not db.save_product(code, name, qty, price):
                messagebox.showerror("Error", f"Product code '{code}' already exists.")
                return
            self.inventory_tree.insert('', 'end', values=(code, name, qty, price))
            win.destroy()

        entries[-1].bind("<Return>", lambda e: save())
        tk.Button(frame, text="Save", command=save, width=7, height=3,
                  font=("Arial", 10), foreground="white", bg="#3979B4").pack(pady=10)

    def edit_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return

        old_values = self.inventory_tree.item(selected)["values"]

        win = tk.Toplevel()
        win.title("Edit Product")
        win.geometry("600x400")
        win.iconbitmap("../assets/edit_product.ico")

        frame = tk.Frame(win, padx=70, pady=20, bg="light grey")
        frame.pack(expand=True)
        tk.Label(frame, text="EDIT PRODUCT", font=("Helvetica", 16),
                 bg="light grey").pack(side=tk.TOP, pady=10)

        labels = ("Product Code", "Product Name", "Quantity", "Unit Price")
        fields = {}
        for label, val in zip(labels, old_values):
            tk.Label(frame, text=f"{label}:", bg="light grey").pack(padx=10, pady=5)
            entry = tk.Entry(frame, bg="#F4F4F4")
            entry.pack(padx=10, pady=5)
            entry.insert(0, val)
            fields[label] = entry

        entries = list(fields.values())
        entries[0].focus_set()
        for i in range(len(entries) - 1):
            entries[i].bind("<Return>", lambda e, nxt=entries[i + 1]: nxt.focus_set())

        def save_changes():
            new_code  = fields["Product Code"].get().strip()
            new_name  = fields["Product Name"].get().strip()
            new_qty   = fields["Quantity"].get().strip()
            new_price = fields["Unit Price"].get().strip()
            try:
                new_qty, new_price = int(new_qty), float(new_price)
            except ValueError:
                messagebox.showerror("Error", "Quantity must be an integer and Unit Price a number.")
                return
            db.update_product(str(old_values[0]), new_code, new_name, new_qty, new_price)
            self.inventory_tree.item(selected, values=(new_code, new_name, new_qty, new_price))
            win.destroy()

        entries[-1].bind("<Return>", lambda e: save_changes())
        tk.Button(frame, text="Save", command=save_changes, width=7, height=3,
                  font=("Arial", 10), foreground="white", bg="#3979B4").pack(pady=10)

    def delete_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        code = self.inventory_tree.item(selected)["values"][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            db.delete_product(str(code))
            self.inventory_tree.delete(selected)

    def search_product(self):
        term = self.search_entry.get().strip()
        if not term:
            messagebox.showerror("Error", "Please enter a product name to search.")
            return
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for row in db.find_product_by_name(term):
            self.inventory_tree.insert('', 'end',
                                       values=(row["product_code"], row["product_name"],
                                               row["quantity"], row["unit_price"]))

    def show_all_products(self):
        self.load_products()

    def export_to_excel(self):
        filename = f"inventory_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        if not filepath:
            return

        wb = Workbook()
        ws = wb.active
        ws.append(["Product Code", "Product Name", "Quantity", "Unit Price"])
        for row_id in self.inventory_tree.get_children():
            ws.append(list(self.inventory_tree.item(row_id)["values"]))
        wb.save(filepath)
        messagebox.showinfo("Success", "Data exported successfully!")


def create_inventory_frame(parent, root):
    frame = InventoryFrame(parent, root)
    frame.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return frame
