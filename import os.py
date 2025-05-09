import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import locale
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image

# Establecer la configuración regional para el formato de números español
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

class FacturaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Facturas GALL S.L")
        self.geometry("850x650")

        self.logo_path = "LOGO.jpeg"
        self.cliente_data = {}
        self.articulos = []

        self.create_cliente_form()
        self.create_articulos_table()
        self.create_buttons()

    def format_number(self, number):
        return locale.format_string("%.2f", number, grouping=True)

    def create_cliente_form(self):
        cliente_frame = ttk.LabelFrame(self, text="Datos del Cliente")
        cliente_frame.pack(padx=10, pady=10, fill=tk.X)

        labels = ["Nombre Completo", "Documento", "Dirección", "Email", "Teléfono"]
        for i, label_text in enumerate(labels):
            label = ttk.Label(cliente_frame, text=label_text + ":")
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(cliente_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            self.cliente_data[label_text] = entry

        cliente_frame.columnconfigure(1, weight=1)

    def create_articulos_table(self):
        self.tree = ttk.Treeview(self, columns=("Descripcion", "Cantidad", "Unidad", "Precio Unitario", "Precio"), show="headings")
        self.tree.heading("Descripcion", text="Descripción")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Unidad", text="Unidad")
        self.tree.heading("Precio Unitario", text="Precio Unitario")
        self.tree.heading("Precio", text="Precio")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_buttons(self):
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar Artículo", command=self.add_articulo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Artículo", command=self.edit_articulo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Artículo", command=self.delete_articulo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generar PDF", command=self.generate_pdf).pack(side=tk.LEFT, padx=5)

    def add_articulo(self):
        def save_articulo():
            descripcion = descripcion_entry.get()
            cantidad = float(cantidad_entry.get())
            unidad = unidad_entry.get()
            precio_unitario = float(precio_unitario_entry.get())
            total = cantidad * precio_unitario
            self.articulos.append({"Descripcion": descripcion, "Cantidad": cantidad, "Unidad": unidad, "Precio Unitario": precio_unitario, "Total": total})
            self.tree.insert("", tk.END, values=(descripcion, cantidad, unidad, self.format_number(precio_unitario), self.format_number(total)))
            add_dialog.destroy()

        add_dialog = tk.Toplevel(self)
        add_dialog.title("Agregar Artículo")

        tk.Label(add_dialog, text="Descripción:").grid(row=0, column=0, padx=5, pady=5)
        descripcion_entry = tk.Entry(add_dialog)
        descripcion_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_dialog, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        cantidad_entry = tk.Entry(add_dialog)
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_dialog, text="Unidad:").grid(row=2, column=0, padx=5, pady=5)
        unidad_entry = tk.Entry(add_dialog)
        unidad_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_dialog, text="Precio Unitario:").grid(row=3, column=0, padx=5, pady=5)
        precio_unitario_entry = tk.Entry(add_dialog)
        precio_unitario_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(add_dialog, text="Guardar", command=save_articulo).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def edit_articulo(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para editar.")
            return

        item_data = self.tree.item(selected_item, 'values')

        def save_edit():
            descripcion = descripcion_entry.get()
            cantidad = float(cantidad_entry.get())
            unidad = unidad_entry.get()
            precio_unitario = float(precio_unitario_entry.get())
            total = cantidad * precio_unitario

            self.tree.item(selected_item, values=(descripcion, cantidad, unidad, self.format_number(precio_unitario), self.format_number(total)))
            index = self.tree.index(selected_item)
            self.articulos[index] = {"Descripcion": descripcion, "Cantidad": cantidad, "Unidad": unidad, "Precio Unitario": precio_unitario, "Total": total}
            edit_dialog.destroy()

        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("Editar Artículo")

        tk.Label(edit_dialog, text="Descripción:").grid(row=0, column=0, padx=5, pady=5)
        descripcion_entry = tk.Entry(edit_dialog)
        descripcion_entry.insert(0, item_data[0])
        descripcion_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        cantidad_entry = tk.Entry(edit_dialog)
        cantidad_entry.insert(0, item_data[1])
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Unidad:").grid(row=2, column=0, padx=5, pady=5)
        unidad_entry = tk.Entry(edit_dialog)
        unidad_entry.insert(0, item_data[2])
        unidad_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Precio Unitario:").grid(row=3, column=0, padx=5, pady=5)
        precio_unitario_entry = tk.Entry(edit_dialog)
        precio_unitario_entry.insert(0, item_data[3])
        precio_unitario_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(edit_dialog, text="Guardar", command=save_edit).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def delete_articulo(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar.")
            return
        self.tree.delete(selected_item)
        index = self.tree.index(selected_item)
        del self.articulos[index]
    def generate_pdf(self):
        try:
            c = canvas.Canvas("factura_gall_sl.pdf", pagesize=letter)
            styles = getSampleStyleSheet()
            normal_style = styles['Normal']
            from reportlab.lib.styles import ParagraphStyle
            bold_style = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

            address_style = styles['Normal']
            address_style.leading = 12

            # --- Logo en la esquina superior derecha ---
            try:
                img = Image.open(self.logo_path)
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                logo_width = 1.5 * inch
                logo_height = logo_width * aspect_ratio
                c.drawImage(self.logo_path, 6.5 * inch, 10.5 * inch, width=logo_width, height=logo_height)
            except FileNotFoundError:
                print(f"Error: El logo no se encontró en la ruta: {self.logo_path}")
                c.drawString(6.5 * inch, 10.5 * inch, "Logo de la Empresa")

            # --- Datos de la empresa ---
            empresa_x = 1 * inch
            y = 10.3 * inch
            line_height = 0.2 * inch

            empresa_nombre = Paragraph("SATE CONSTRUCCIONES Y CONTRATAS GALL SL", bold_style)
            w, h = empresa_nombre.wrapOn(c, 3 * inch, 1 * inch)
            empresa_nombre.drawOn(c, empresa_x, y)
            y -= h

            p = Paragraph("Dirección: C/CAPITAN CORTEZ 34 1B", normal_style)
            w, h = p.wrapOn(c, 3 * inch, 1 * inch)
            p.drawOn(c, empresa_x, y - 2)
            y -= h + 2

            c.setFont("Helvetica", 10)
            c.drawString(empresa_x, y, "NIF: B21775614")
            y -= line_height
            c.drawString(empresa_x, y, "Teléfono: 642 96 00 94")
            y -= line_height
            c.drawString(empresa_x, y, "Email: ")
            y -= line_height * 1.5

            # --- Datos del cliente ---
            cliente_label = Paragraph("Cliente:", bold_style)
            w, h = cliente_label.wrapOn(c, 3.5 * inch, 1 * inch)
            cliente_label.drawOn(c, empresa_x, y)
            y -= h

            c.setFont("Helvetica", 10)
            c.drawString(empresa_x, y, "Nombre: " + self.cliente_data["Nombre Completo"].get())
            y -= line_height
            c.drawString(empresa_x, y, "Documento: " + self.cliente_data["Documento"].get())
            y -= line_height
            direccion_cliente = self.cliente_data["Dirección"].get()
            p = Paragraph("Dirección: " + direccion_cliente, address_style)
            p.wrapOn(c, 3.5 * inch, 0.5 * inch)
            p.drawOn(c, empresa_x, y - p.height)
            y -= (line_height + p.height - 6)
            c.drawString(empresa_x, y, "Teléfono: " + self.cliente_data["Teléfono"].get())
            y -= line_height
            c.drawString(empresa_x, y, "Email: " + self.cliente_data["Email"].get())

            # --- Tabla de artículos ---
            table_x_offset = 1 * inch
            data = [["Descripción", "Cantidad", "Unidad", "Precio Unitario", "Precio"]]
            for item in self.articulos:
                data.append([
                    item["Descripcion"],
                    str(item["Cantidad"]),
                    item["Unidad"],
                    self.format_number(item["Precio Unitario"]),
                    self.format_number(item["Total"])
                ])

            col_widths = [2.5 * inch, 0.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch]
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            table_y_position = 4.5 * inch
            table.wrapOn(c, 7 * inch, 8 * inch)
            table.drawOn(c, table_x_offset, table_y_position)

            # --- Totales ---
            total = sum(item["Total"] for item in self.articulos)
            iva = total * 0.21
            total_con_iva = total + iva

            c.setFont("Helvetica-Bold", 10)
            right_x = table_x_offset + sum(col_widths)

            c.drawRightString(right_x - 5, table_y_position - 20, "Subtotal:")
            c.drawRightString(right_x, table_y_position - 20, self.format_number(total))

            c.drawRightString(right_x - 5, table_y_position - 40, "IVA (21%):")
            c.drawRightString(right_x, table_y_position - 40, self.format_number(iva))

            c.drawRightString(right_x - 5, table_y_position - 60, "Total con IVA:")
            c.drawRightString(right_x, table_y_position - 60, self.format_number(total_con_iva))

            c.save()
            messagebox.showinfo("Factura Generada", "La factura se ha generado correctamente como factura_gall_sl.pdf")

        except Exception as e:
            messagebox.showerror("Error al Generar PDF", f"Ocurrió un error al generar el PDF: {e}")
