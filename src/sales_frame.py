import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import Calendar
from openpyxl import Workbook
import database as db


class SalesFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg="light grey")
        self.root = root

        # ── Left: treeview ───────────────────────────────────────────────────
        data_frame = tk.Frame(self, bg="light grey")
        data_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        tk.Label(data_frame, text="SALES", bg="light grey",
                 font=("Helvetica", 18, "bold")).pack(side=tk.TOP, pady=10)

        tk.Button(self, text="<<", command=self.go_back,
                  height=2, width=8, font=("Helvetica", 15)).pack(
            side=tk.LEFT, padx=20, pady=20)

        cols = ("Receipt", "Date", "Customer ID", "Customer Name", "Description", "Total")
        widths = (80, 130, 90, 150, 330, 100)
        self.sales_tree = ttk.Treeview(data_frame, columns=cols, show='headings')
        for col, w in zip(cols, widths):
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=w)

        scrollbar = tk.Scrollbar(data_frame, orient="vertical",
                                 command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sales_tree.pack(side=tk.LEFT, fill=tk.Y)

        # ── Right: buttons + calendar ────────────────────────────────────────
        btn_frame = tk.Frame(self, bg="light grey")
        btn_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=95, pady=50)

        btn_cfg = dict(height=4, width=15, foreground="white",
                       bg="#3979B4", font=("Arial", 12))
        tk.Button(btn_frame, text="Add Sale",
                  command=self.add_sale, **btn_cfg).pack(padx=30)
        tk.Button(btn_frame, text="Edit Sale",
                  command=self.edit_sale, **btn_cfg).pack(pady=10, padx=30)

        tk.Label(btn_frame, text=" ", bg="light grey").pack(pady=5)

        tk.Label(btn_frame, text="Select Date", bg="light grey").pack(pady=5)
        self.calendar = Calendar(btn_frame, selectmode='day', date_pattern='y-mm-dd')
        self.calendar.pack(pady=5, padx=30)
        self.calendar.bind("<<CalendarSelected>>", self.update_revenue_by_date)

        tk.Button(btn_frame, text="Export Sales by Date",
                  command=self.export_to_excel,
                  height=2, width=17, foreground="white",
                  bg="#3979B4", font=("Arial", 10)).pack(pady=15, padx=30)
        tk.Button(btn_frame, text="Export All Sales",
                  command=self.export_all_to_excel,
                  height=2, width=17, foreground="white",
                  bg="#3979B4", font=("Arial", 10)).pack(pady=5, padx=30)

        tk.Label(btn_frame, text=" ", bg="light grey").pack(pady=10)

        self.total_revenue_var = tk.StringVar(value="0")
        tk.Label(btn_frame, text="Total Revenue: G.", bg="light grey",
                 font=("Arial", 13, "bold")).pack(pady=5)
        tk.Label(btn_frame, textvariable=self.total_revenue_var, bg="light grey",
                 font=("Arial", 13, "bold")).pack(padx=30)

        self.receipt_number = db.get_next_receipt_number()
        self.update_revenue_by_date()
        self.load_sales()

    def go_back(self):
        self.root.show_frame("Options")

    def load_sales(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        for row in db.get_all_sales():
            self.sales_tree.insert("", tk.END, values=(
                row["receipt_no"], row["date"], row["customer_id"],
                row["customer_name"], row["description"], row["total"]
            ))

    def update_revenue_by_date(self, event=None):
        selected_date = self.calendar.get_date()
        total = db.get_revenue_by_date(selected_date)
        self.total_revenue_var.set(str(int(total)))

    # ── Add Sale ──────────────────────────────────────────────────────────────

    def add_sale(self):
        win = tk.Toplevel()
        win.title("Add Sale")
        win.geometry("800x750")
        win.iconbitmap("../assets/sales.ico")

        # Receipt (read-only)
        tk.Label(win, text="Receipt No.").pack(pady=5)
        receipt_var = tk.IntVar(value=self.receipt_number)
        tk.Entry(win, textvariable=receipt_var, state='readonly').pack(pady=5)

        # Customer
        tk.Label(win, text="Customer ID:").pack(pady=5)
        customer_id_entry = tk.Entry(win)
        customer_id_entry.pack(pady=5)

        tk.Label(win, text="Customer Name:").pack(pady=5)
        customer_name_var = tk.StringVar()
        tk.Entry(win, textvariable=customer_name_var).pack(pady=5)

        def search_customer():
            cid = customer_id_entry.get().strip()
            row = db.find_customer(cid)
            if row:
                customer_id_entry.delete(0, tk.END)
                customer_id_entry.insert(0, row["id_number"])
                customer_name_var.set(row["name"])
            else:
                customer_name_var.set("Customer not found")

        tk.Button(win, text="Search Customer", command=search_customer,
                  font=("Arial", 10), bg="light grey").pack(pady=5)

        # Product search row
        product_frame = tk.Frame(win)
        product_frame.pack(pady=5)

        tk.Label(product_frame, text="Product Code:").grid(row=0, column=0, padx=5)
        product_code_entry = tk.Entry(product_frame)
        product_code_entry.grid(row=0, column=1, padx=5)

        tk.Label(product_frame, text="Product Name:").grid(row=0, column=2, padx=5)
        product_name_var = tk.StringVar()
        tk.Entry(product_frame, textvariable=product_name_var,
                 state='readonly').grid(row=0, column=3, padx=5)

        tk.Label(product_frame, text="Quantity:").grid(row=0, column=4, padx=5)
        quantity_entry = tk.Entry(product_frame)
        quantity_entry.grid(row=0, column=5, padx=5)

        tk.Label(product_frame, text="Unit Price:").grid(row=1, column=0, padx=5)
        unit_price_entry = tk.Entry(product_frame)
        unit_price_entry.grid(row=1, column=1, padx=5)

        def search_product(event=None):
            row = db.find_product_by_code(product_code_entry.get().strip())
            if row:
                product_name_var.set(row["product_name"])
                unit_price_entry.delete(0, tk.END)
                unit_price_entry.insert(0, str(int(row["unit_price"])))
            else:
                product_name_var.set("Product not found")
                unit_price_entry.delete(0, tk.END)

        product_code_entry.bind("<Return>", search_product)

        # Products treeview
        cols = ("Quantity", "Product Name", "Unit Price", "Subtotal")
        products_tree = ttk.Treeview(win, columns=cols, show='headings')
        for col in cols:
            products_tree.heading(col, text=col)
            products_tree.column(col, width=140)
        products_tree.pack(expand=True, fill=tk.BOTH, pady=20)

        total_var = tk.StringVar(value="0")

        def add_product():
            try:
                qty   = int(quantity_entry.get())
                price = int(unit_price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Quantity and Unit Price must be numbers.")
                return
            name     = product_name_var.get()
            subtotal = qty * price

            row = db.find_product_by_code(product_code_entry.get().strip())
            if row and row["quantity"] < qty:
                messagebox.showerror("Error", f"Not enough stock for '{name}'.")
                return

            products_tree.insert("", tk.END, values=(qty, name, price, subtotal))
            total_var.set(str(int(total_var.get()) + subtotal))

            for e in (quantity_entry, product_code_entry, unit_price_entry):
                e.delete(0, tk.END)
            product_name_var.set("")

        tk.Button(product_frame, text="Add Product", command=add_product,
                  font=("Arial", 10), foreground="white",
                  bg="#3979B4").grid(row=0, column=6, padx=5)

        total_frame = tk.Frame(win)
        total_frame.pack(pady=5)
        tk.Label(total_frame, text="Total: G.",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
        tk.Entry(total_frame, textvariable=total_var, state='readonly',
                 font=("Arial", 12)).grid(row=0, column=1, padx=5)

        def save_sale():
            products_sold = [
                {
                    "quantity":     int(products_tree.item(r)["values"][0]),
                    "product_name": products_tree.item(r)["values"][1],
                    "unit_price":   int(products_tree.item(r)["values"][2]),
                    "subtotal":     int(products_tree.item(r)["values"][3]),
                }
                for r in products_tree.get_children()
            ]
            if not products_sold:
                messagebox.showwarning("Warning", "Please add at least one product.")
                return

            receipt_no    = receipt_var.get()
            date          = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            customer_id   = customer_id_entry.get().strip()
            customer_name = customer_name_var.get()
            total         = int(total_var.get())
            description   = "; ".join(
                f"{p['quantity']} x {p['product_name']} @ {p['unit_price']}"
                for p in products_sold
            )

            db.save_sale(receipt_no, date, customer_id, customer_name, description, total)
            for p in products_sold:
                db.decrease_product_quantity(p["product_name"], p["quantity"])

            self.sales_tree.insert("", tk.END,
                                   values=(receipt_no, date, customer_id,
                                           customer_name, description, total))
            self.receipt_number += 1
            self.update_revenue_by_date()
            win.destroy()

        tk.Button(total_frame, text="Save Sale", command=save_sale,
                  font=("Arial", 12), foreground="white",
                  bg="#3979B4").grid(row=0, column=2, padx=10)

        customer_id_entry.focus_set()
        customer_id_entry.bind("<Return>", lambda e: search_customer())

    # ── Edit Sale ─────────────────────────────────────────────────────────────

    def edit_sale(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a sale to edit.")
            return

        sale_values = self.sales_tree.item(selected)["values"]

        win = tk.Toplevel()
        win.title("Edit Sale")
        win.geometry("800x700")
        win.iconbitmap("../assets/sales.ico")

        tk.Label(win, text="Receipt No.").pack(pady=5)
        receipt_var = tk.IntVar(value=sale_values[0])
        tk.Entry(win, textvariable=receipt_var, state='readonly').pack(pady=5)

        tk.Label(win, text="Customer ID:").pack(pady=5)
        customer_id_var = tk.StringVar(value=sale_values[2])
        customer_id_entry = tk.Entry(win, textvariable=customer_id_var)
        customer_id_entry.pack(pady=5)

        tk.Label(win, text="Customer Name:").pack(pady=5)
        customer_name_var = tk.StringVar(value=sale_values[3])
        tk.Entry(win, textvariable=customer_name_var).pack(pady=5)

        def search_customer():
            row = db.find_customer(customer_id_var.get().strip())
            if row:
                customer_name_var.set(row["name"])
            else:
                customer_name_var.set("Customer not found")

        tk.Button(win, text="Search Customer", command=search_customer,
                  font=("Arial", 10), bg="light grey").pack(pady=5)

        # Product row
        product_frame = tk.Frame(win)
        product_frame.pack(pady=5)

        tk.Label(product_frame, text="Product Code:").grid(row=0, column=0, padx=5)
        product_code_entry = tk.Entry(product_frame)
        product_code_entry.grid(row=0, column=1, padx=5)

        tk.Label(product_frame, text="Product Name:").grid(row=0, column=2, padx=5)
        product_name_var = tk.StringVar()
        tk.Entry(product_frame, textvariable=product_name_var,
                 state='readonly').grid(row=0, column=3, padx=5)

        tk.Label(product_frame, text="Quantity:").grid(row=0, column=4, padx=5)
        quantity_entry = tk.Entry(product_frame)
        quantity_entry.grid(row=0, column=5, padx=10)

        tk.Label(product_frame, text="Unit Price:").grid(row=1, column=2, padx=5, pady=10)
        unit_price_entry = tk.Entry(product_frame)
        unit_price_entry.grid(row=1, column=3, padx=5, pady=10)

        def search_product_edit(event=None):
            row = db.find_product_by_code(product_code_entry.get().strip())
            if row:
                product_name_var.set(row["product_name"])
                unit_price_entry.delete(0, tk.END)
                unit_price_entry.insert(0, str(int(row["unit_price"])))
            else:
                product_name_var.set("Product not found")
                unit_price_entry.delete(0, tk.END)

        product_code_entry.bind("<Return>", search_product_edit)

        cols = ("Quantity", "Product Name", "Unit Price", "Subtotal")
        products_tree = ttk.Treeview(win, columns=cols, show='headings')
        for col in cols:
            products_tree.heading(col, text=col)
            products_tree.column(col, width=150)
        products_tree.pack(expand=True, fill='both', pady=20)

        total_var = tk.StringVar(value=str(sale_values[5]))

        # Populate existing products
        products_edit = []
        for item in str(sale_values[4]).split("; "):
            try:
                qty_str, rest   = item.split(" x ")
                name, price_str = rest.split(" @ ")
                qty   = int(qty_str)
                price = int(price_str)
                sub   = qty * price
                products_edit.append({"product_name": name, "quantity": qty,
                                      "unit_price": price, "subtotal": sub})
                products_tree.insert("", tk.END, values=(qty, name, price, sub))
            except ValueError:
                pass

        def add_product_edit():
            try:
                qty   = int(quantity_entry.get())
                price = int(unit_price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Quantity and Unit Price must be numbers.")
                return
            name     = product_name_var.get()
            subtotal = qty * price
            products_tree.insert("", tk.END, values=(qty, name, price, subtotal))
            total_var.set(str(int(total_var.get()) + subtotal))
            products_edit.append({"product_name": name, "quantity": qty,
                                  "unit_price": price, "subtotal": subtotal})
            db.decrease_product_quantity(name, qty)

        def delete_product_edit():
            sel = products_tree.selection()
            if not sel:
                messagebox.showerror("Error", "Please select a product to delete.")
                return
            vals = products_tree.item(sel)["values"]
            db.increase_product_quantity(vals[1], int(vals[0]))
            total_var.set(str(int(total_var.get()) - int(vals[3])))
            products_tree.delete(sel)

        tk.Button(product_frame, text="Add Product", command=add_product_edit,
                  font=("Arial", 10), foreground="white",
                  bg="#3979B4").grid(row=0, column=6, padx=10, pady=5)
        tk.Button(product_frame, text="Delete Product", command=delete_product_edit,
                  font=("Arial", 10), foreground="white",
                  bg="#3979B4").grid(row=1, column=6, padx=10)

        def fill_fields(event):
            sel = products_tree.selection()
            if not sel:
                return
            vals = products_tree.item(sel)["values"]
            product_name_var.set(vals[1])
            quantity_entry.delete(0, tk.END)
            quantity_entry.insert(0, vals[0])
            unit_price_entry.delete(0, tk.END)
            unit_price_entry.insert(0, vals[2])

        products_tree.bind("<ButtonRelease-1>", fill_fields)

        total_frame = tk.Frame(win)
        total_frame.pack(pady=5)
        tk.Label(total_frame, text="Total: G.",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
        tk.Entry(total_frame, textvariable=total_var, state='readonly',
                 font=("Arial", 12)).grid(row=0, column=1, padx=5)

        def save_changes():
            new_customer_id   = customer_id_var.get().strip()
            new_customer_name = customer_name_var.get().strip()
            updated_products  = [
                f"{products_tree.item(r)['values'][0]} x "
                f"{products_tree.item(r)['values'][1]} @ "
                f"{products_tree.item(r)['values'][2]}"
                for r in products_tree.get_children()
            ]
            new_description = "; ".join(updated_products)
            new_total       = int(total_var.get())
            receipt_no      = receipt_var.get()

            db.update_sale(receipt_no, new_customer_id, new_customer_name,
                           new_description, new_total)
            self.sales_tree.item(selected, values=(
                receipt_no, sale_values[1], new_customer_id,
                new_customer_name, new_description, new_total
            ))
            self.update_revenue_by_date()
            win.destroy()

        tk.Button(total_frame, text="Save Changes", command=save_changes,
                  font=("Arial", 12), foreground="white",
                  bg="#3979B4").grid(row=0, column=2, padx=10)

    # ── Export ────────────────────────────────────────────────────────────────

    def export_to_excel(self):
        selected_date = self.calendar.get_date()
        rows = db.get_sales_by_date(selected_date)
        if not rows:
            messagebox.showinfo("No Data", f"No sales found for {selected_date}.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"sales_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Sales Data"
        ws.append(["Receipt No", "Date", "Customer ID",
                   "Customer Name", "Description", "Total"])
        for row in rows:
            ws.append([row["receipt_no"], row["date"], row["customer_id"],
                       row["customer_name"], row["description"], row["total"]])
        wb.save(path)
        messagebox.showinfo("Success", f"Exported to {path}")

    def export_all_to_excel(self):
        rows = db.get_all_sales()
        if not rows:
            messagebox.showerror("Error", "No sales data to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="all_sales.xlsx"
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Sales Data"
        ws.append(["Receipt No", "Date", "Customer ID",
                   "Customer Name", "Description", "Total"])
        for row in rows:
            ws.append([row["receipt_no"], row["date"], row["customer_id"],
                       row["customer_name"], row["description"], row["total"]])
        wb.save(path)
        messagebox.showinfo("Success", f"Exported to {path}")


def create_sales_frame(parent, root):
    frame = SalesFrame(parent, root)
    frame.grid(row=0, column=0, sticky="nsew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return frame
