import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from collections import defaultdict
import csv

class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS System")
        self.geometry("900x600")
        self.configure(bg="#2E2E2E")

        # Data Structures
        self.till = 500.00
        self.items = {"Shoes": {"price": 5.50, "stock": 20},
                      "Hat":   {"price": 7.60, "stock": 15},
                      "Socks": {"price": 8.15, "stock": 30}}
        self.sales_record = defaultdict(int)

        # Style
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#2E2E2E")
        self.style.configure("TNotebook.Tab", background="#444", foreground="white", padding=10)
        self.style.map("TNotebook.Tab", background=[('selected', '#666')])
        self.style.configure("Treeview", background="#3E3E3E", fieldbackground="#3E3E3E", foreground="white")
        self.style.configure("TButton", background="#555", foreground="white", padding=5)

        # Notebook Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_reports_tab()
        self.create_status_bar()

    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sales")

        frame = tk.Frame(tab, bg="#2E2E2E")
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(frame, text="Select Item:", bg="#2E2E2E", fg="white").grid(row=0, column=0, sticky="w")
        self.selected_item = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.selected_item, values=list(self.items.keys()), state="readonly").grid(row=0, column=1)

        tk.Label(frame, text="Quantity:", bg="#2E2E2E", fg="white").grid(row=1, column=0, sticky="w")
        self.quantity_var = tk.IntVar(value=1)
        tk.Spinbox(frame, from_=1, to=100, textvariable=self.quantity_var, width=5).grid(row=1, column=1)

        tk.Label(frame, text="Cash Given:", bg="#2E2E2E", fg="white").grid(row=2, column=0, sticky="w")
        self.cash_var = tk.DoubleVar(value=0.0)
        tk.Entry(frame, textvariable=self.cash_var).grid(row=2, column=1)

        ttk.Button(frame, text="Process Sale", command=self.process_sale).grid(row=3, column=0, columnspan=2, pady=10)

    def create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventory")

        frame = tk.Frame(tab, bg="#2E2E2E")
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        cols = ("Item", "Price", "Stock")
        self.inv_tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)
        for c in cols:
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=200)
        self.inv_tree.pack(side='left', fill='both', expand=True)
        self.refresh_inventory()

        btn_frame = tk.Frame(frame, bg="#2E2E2E")
        btn_frame.pack(side='right', fill='y', padx=10)

        ttk.Button(btn_frame, text="Add Item", command=self.add_item).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Edit Selected", command=self.edit_item).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Restock Selected", command=self.restock_item).pack(fill='x', pady=5)

    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")

        frame = tk.Frame(tab, bg="#2E2E2E")
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        cols = ("Item", "Units Sold")
        self.rep_tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)
        for c in cols:
            self.rep_tree.heading(c, text=c)
            self.rep_tree.column(c, width=300)
        self.rep_tree.pack(side='left', fill='both', expand=True)
        self.refresh_reports()

        btn_frame = tk.Frame(frame, bg="#2E2E2E")
        btn_frame.pack(side='right', fill='y', padx=10)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(fill='x', pady=5)

    def create_status_bar(self):
        self.status = tk.Label(self, text=f"Till: ${self.till:.2f}", bd=1, relief='sunken', anchor='e', bg="#1C1C1C", fg="white")
        self.status.pack(side='bottom', fill='x')

    def process_sale(self):
        item = self.selected_item.get()
        qty = self.quantity_var.get()
        cash = self.cash_var.get()
        if item not in self.items:
            messagebox.showerror("Error", "Please select a valid item.")
            return
        total = self.items[item]['price'] * qty
        if cash < total:
            messagebox.showwarning("Insufficient Funds", f"Total cost is ${total:.2f}. Please collect more cash.")
            return
        if self.items[item]['stock'] < qty:
            messagebox.showwarning("Out of Stock", f"Only {self.items[item]['stock']} left in stock.")
            return
        # Update records
        change = cash - total
        self.till += total
        self.items[item]['stock'] -= qty
        self.sales_record[item] += qty
        messagebox.showinfo("Sale Complete", f"Change due: ${change:.2f}")
        self.cash_var.set(0.0)
        self.quantity_var.set(1)
        self.refresh_inventory()
        self.refresh_reports()
        self.update_status()

    def add_item(self):
        name = simpledialog.askstring("New Item", "Enter item name:")
        if not name:
            return
        price = simpledialog.askfloat("New Item", f"Enter price for '{name}':")
        stock = simpledialog.askinteger("New Item", f"Enter starting stock for '{name}':")
        self.items[name] = {'price': price, 'stock': stock}
        self.refresh_inventory()

    def edit_item(self):
        sel = self.inv_tree.selection()
        if not sel:
            return
        name = self.inv_tree.item(sel[0], 'values')[0]
        price = simpledialog.askfloat("Edit Price", f"New price for '{name}':", initialvalue=self.items[name]['price'])
        self.items[name]['price'] = price
        self.refresh_inventory()
        self.refresh_reports()

    def restock_item(self):
        sel = self.inv_tree.selection()
        if not sel:
            return
        name = self.inv_tree.item(sel[0], 'values')[0]
        inc = simpledialog.askinteger("Restock", f"Add how many units of '{name}'?", minvalue=1)
        self.items[name]['stock'] += inc
        self.refresh_inventory()
        self.update_status()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Item','Units Sold'])
            for item, sold in self.sales_record.items():
                writer.writerow([item, sold])
        messagebox.showinfo("Export Complete", f"Report saved to {path}")

    def refresh_inventory(self):
        for i in self.inv_tree.get_children():
            self.inv_tree.delete(i)
        for name, data in self.items.items():
            self.inv_tree.insert('', 'end', values=(name, f"${data['price']:.2f}", data['stock']))

    def refresh_reports(self):
        for i in self.rep_tree.get_children():
            self.rep_tree.delete(i)
        for name, sold in self.sales_record.items():
            self.rep_tree.insert('', 'end', values=(name, sold))

    def update_status(self):
        self.status.config(text=f"Till: ${self.till:.2f}")

if __name__ == '__main__':
    app = POSApp()
    app.mainloop()
