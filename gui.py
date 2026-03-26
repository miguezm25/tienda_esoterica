import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from inventario import Producto, Inventario
from PIL import Image, ImageTk


class InventarioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tienda Esotérica - Sistema de Inventario")
        self.root.geometry("1360x760")
        self.root.minsize(1280, 720)
        self.root.resizable(True, True)

        self.inventario = Inventario("tienda_esoterica.db")
        self.thumbnail = None
        self.ruta_imagen = ""
        self.modo_edicion = False

        self.preview_width = 220
        self.preview_height = 220

        self.carpeta_imagenes = "imagenes_productos"
        os.makedirs(self.carpeta_imagenes, exist_ok=True)

        self.crear_widgets()
        self.cargar_categorias()
        self.cargar_productos()

    def crear_widgets(self):
        frame_formulario = tk.LabelFrame(self.root, text="Gestión de Productos", padx=10, pady=10)
        frame_formulario.place(x=20, y=20, width=430, height=700)

        tk.Label(frame_formulario, text="Código").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_codigo = tk.Entry(frame_formulario, width=30)
        self.entry_codigo.grid(row=0, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(frame_formulario, text="Nombre").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_nombre = tk.Entry(frame_formulario, width=30)
        self.entry_nombre.grid(row=1, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(frame_formulario, text="Categoría").grid(row=2, column=0, sticky="w", pady=4)
        self.combo_categoria = ttk.Combobox(frame_formulario, width=27, state="readonly")
        self.combo_categoria.grid(row=2, column=1, sticky="w", pady=4)

        frame_categoria_botones = tk.Frame(frame_formulario)
        frame_categoria_botones.grid(row=2, column=2, padx=4, pady=4)

        tk.Button(frame_categoria_botones, text="Nueva", width=8, command=self.agregar_categoria).grid(row=0, column=0, padx=2)
        tk.Button(frame_categoria_botones, text="Eliminar", width=8, command=self.eliminar_categoria).grid(row=0, column=1, padx=2)

        tk.Label(frame_formulario, text="Precio").grid(row=3, column=0, sticky="w", pady=4)
        self.entry_precio = tk.Entry(frame_formulario, width=30)
        self.entry_precio.grid(row=3, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(frame_formulario, text="Cantidad").grid(row=4, column=0, sticky="w", pady=4)
        self.entry_cantidad = tk.Entry(frame_formulario, width=30)
        self.entry_cantidad.grid(row=4, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(frame_formulario, text="Descripción").grid(row=5, column=0, sticky="nw", pady=4)
        self.text_descripcion = tk.Text(frame_formulario, width=28, height=4)
        self.text_descripcion.grid(row=5, column=1, columnspan=2, sticky="w", pady=4)

        tk.Label(frame_formulario, text="Características").grid(row=6, column=0, sticky="nw", pady=4)
        self.text_caracteristicas = tk.Text(frame_formulario, width=28, height=4)
        self.text_caracteristicas.grid(row=6, column=1, columnspan=2, sticky="w", pady=4)

        tk.Button(frame_formulario, text="Imagen", width=10, command=self.seleccionar_imagen).grid(row=7, column=0, pady=6)
        self.label_imagen_ruta = tk.Label(frame_formulario, text="Sin imagen", anchor="w", width=28)
        self.label_imagen_ruta.grid(row=7, column=1, columnspan=2, sticky="w")

        self.canvas_preview = tk.Canvas(
            frame_formulario,
            width=self.preview_width,
            height=self.preview_height,
            bg="#d9d9d9",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas_preview.grid(row=8, column=1, columnspan=2, pady=8)
        self.canvas_preview.create_text(
            self.preview_width // 2,
            self.preview_height // 2,
            text="Vista previa"
        )

        frame_botones = tk.Frame(frame_formulario)
        frame_botones.grid(row=9, column=0, columnspan=3, pady=10)

        tk.Button(frame_botones, text="Agregar", width=10, command=self.agregar_producto).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(frame_botones, text="Modificar", width=10, command=self.modificar_producto).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(frame_botones, text="Eliminar", width=10, command=self.eliminar_producto).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(frame_botones, text="Vender", width=10, command=self.vender_producto).grid(row=1, column=1, padx=4, pady=4)
        tk.Button(frame_botones, text="Limpiar", width=10, command=self.limpiar_campos).grid(row=1, column=2, padx=4, pady=4)

        frame_busqueda = tk.LabelFrame(self.root, text="Búsqueda y Listado", padx=10, pady=10)
        frame_busqueda.place(x=470, y=20, width=860, height=700)

        tk.Label(frame_busqueda, text="Nombre o código").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        self.entry_busqueda = tk.Entry(frame_busqueda, width=22)
        self.entry_busqueda.grid(row=0, column=1, padx=4, pady=4, sticky="w")

        tk.Button(frame_busqueda, text="Buscar", width=10, command=self.buscar_producto).grid(row=0, column=2, padx=4, pady=4)

        tk.Label(frame_busqueda, text="Categoría").grid(row=0, column=3, padx=4, pady=4, sticky="w")
        self.combo_busqueda_categoria = ttk.Combobox(frame_busqueda, width=20, state="readonly")
        self.combo_busqueda_categoria.grid(row=0, column=4, padx=4, pady=4, sticky="w")

        tk.Button(frame_busqueda, text="Filtrar", width=10, command=self.buscar_por_categoria).grid(row=0, column=5, padx=4, pady=4)
        tk.Button(frame_busqueda, text="Mostrar todos", width=12, command=self.cargar_productos).grid(row=0, column=6, padx=4, pady=4)

        columnas = ("id", "codigo", "nombre", "categoria", "precio", "cantidad")
        self.tree = ttk.Treeview(frame_busqueda, columns=columnas, show="headings", height=28)

        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("cantidad", text="Cantidad")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("codigo", width=90, anchor="center")
        self.tree.column("nombre", width=230)
        self.tree.column("categoria", width=160)
        self.tree.column("precio", width=90, anchor="center")
        self.tree.column("cantidad", width=80, anchor="center")

        self.tree.grid(row=1, column=0, columnspan=7, pady=10, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame_busqueda, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=7, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_producto)

    def cargar_categorias(self):
        categorias = self.inventario.obtener_categorias()
        self.combo_categoria["values"] = categorias
        self.combo_busqueda_categoria["values"] = categorias

        if categorias:
            if not self.combo_categoria.get():
                self.combo_categoria.set(categorias[0])
            if not self.combo_busqueda_categoria.get():
                self.combo_busqueda_categoria.set(categorias[0])

    def agregar_categoria(self):
        nombre = simpledialog.askstring("Nueva categoría", "Ingrese el nombre de la nueva categoría:")
        if nombre:
            exito, mensaje = self.inventario.agregar_categoria(nombre)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_categorias()
                self.combo_categoria.set(nombre)
                self.combo_busqueda_categoria.set(nombre)
            else:
                messagebox.showerror("Error", mensaje)

    def eliminar_categoria(self):
        categoria = self.combo_categoria.get().strip()

        if not categoria:
            messagebox.showwarning("Advertencia", "Seleccione una categoría.")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar",
            f"¿Desea eliminar la categoría '{categoria}'?"
        )

        if not confirmacion:
            return

        exito, mensaje = self.inventario.eliminar_categoria(categoria)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_categorias()

            categorias = self.inventario.obtener_categorias()
            if categorias:
                self.combo_categoria.set(categorias[0])
                self.combo_busqueda_categoria.set(categorias[0])
            else:
                self.combo_categoria.set("")
                self.combo_busqueda_categoria.set("")
        else:
            messagebox.showerror("Error", mensaje)

    def copiar_imagen_al_proyecto(self, ruta_origen, codigo):
        if not ruta_origen or not os.path.exists(ruta_origen):
            return ""

        extension = os.path.splitext(ruta_origen)[1].lower()
        if not extension:
            extension = ".jpg"

        nombre_archivo = f"{codigo}{extension}"
        ruta_destino = os.path.join(self.carpeta_imagenes, nombre_archivo)

        shutil.copy2(ruta_origen, ruta_destino)
        return ruta_destino

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if ruta:
            self.ruta_imagen = ruta
            self.label_imagen_ruta.config(text=os.path.basename(ruta))
            self.mostrar_imagen(ruta)

    def mostrar_imagen(self, ruta):
        try:
            imagen = Image.open(ruta)
            imagen.thumbnail((self.preview_width, self.preview_height))
            self.thumbnail = ImageTk.PhotoImage(imagen)

            self.canvas_preview.delete("all")
            self.canvas_preview.create_image(
                self.preview_width // 2,
                self.preview_height // 2,
                image=self.thumbnail
            )
        except Exception:
            self.canvas_preview.delete("all")
            self.canvas_preview.create_text(
                self.preview_width // 2,
                self.preview_height // 2,
                text="No disponible"
            )

    def obtener_datos_formulario(self):
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        categoria = self.combo_categoria.get().strip()
        precio = self.entry_precio.get().strip()
        cantidad = self.entry_cantidad.get().strip()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        caracteristicas = self.text_caracteristicas.get("1.0", tk.END).strip()

        if not codigo or not nombre or not categoria or not precio or not cantidad:
            raise ValueError("Código, nombre, categoría, precio y cantidad son obligatorios.")

        try:
            precio = float(precio)
        except ValueError:
            raise ValueError("El precio debe ser numérico.")

        try:
            cantidad = int(cantidad)
        except ValueError:
            raise ValueError("La cantidad debe ser un número entero.")

        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")

        return {
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "cantidad": cantidad,
            "descripcion": descripcion,
            "caracteristicas": caracteristicas
        }

    def agregar_producto(self):
        try:
            if self.modo_edicion:
                messagebox.showwarning("Advertencia", "Pulse Limpiar antes de agregar un producto nuevo.")
                return

            datos = self.obtener_datos_formulario()

            ruta_guardada = ""
            if self.ruta_imagen:
                ruta_guardada = self.copiar_imagen_al_proyecto(self.ruta_imagen, datos["codigo"])

            producto = Producto(
                codigo=datos["codigo"],
                nombre=datos["nombre"],
                categoria=datos["categoria"],
                precio=datos["precio"],
                cantidad=datos["cantidad"],
                descripcion=datos["descripcion"],
                caracteristicas=datos["caracteristicas"],
                imagen=ruta_guardada
            )

            exito, mensaje = self.inventario.agregar_producto(producto)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_campos()
                self.cargar_productos()
            else:
                messagebox.showerror("Error", mensaje)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def modificar_producto(self):
        try:
            datos = self.obtener_datos_formulario()

            ruta_guardada = self.ruta_imagen
            if self.ruta_imagen and os.path.exists(self.ruta_imagen):
                if not self.ruta_imagen.startswith(self.carpeta_imagenes):
                    ruta_guardada = self.copiar_imagen_al_proyecto(self.ruta_imagen, datos["codigo"])

            exito, mensaje = self.inventario.modificar_producto(
                datos["codigo"],
                nombre=datos["nombre"],
                categoria=datos["categoria"],
                precio=datos["precio"],
                cantidad=datos["cantidad"],
                descripcion=datos["descripcion"],
                caracteristicas=datos["caracteristicas"],
                imagen=ruta_guardada
            )

            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_campos()
                self.cargar_productos()
            else:
                messagebox.showerror("Error", mensaje)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_producto(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Advertencia", "Seleccione o ingrese el código del producto a eliminar.")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Desea eliminar este producto?")
        if confirmacion:
            exito, mensaje = self.inventario.eliminar_producto(codigo)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_campos()
                self.cargar_productos()
            else:
                messagebox.showerror("Error", mensaje)

    def vender_producto(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Advertencia", "Seleccione primero un producto.")
            return

        cantidad = simpledialog.askinteger("Registrar venta", "¿Cuántas unidades se vendieron?", minvalue=1)
        if cantidad is None:
            return

        exito, mensaje = self.inventario.registrar_venta(codigo, cantidad)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_productos()
            producto = self.inventario.consultar_por_codigo(codigo)
            if producto:
                self.cargar_producto_en_formulario(producto)
        else:
            messagebox.showerror("Error", mensaje)

    def buscar_producto(self):
        termino = self.entry_busqueda.get().strip()
        if not termino:
            self.cargar_productos()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        producto_codigo = self.inventario.consultar_por_codigo(termino)
        resultados_nombre = self.inventario.consultar_por_nombre(termino)

        codigos = set()

        if producto_codigo:
            self.tree.insert("", tk.END, values=producto_codigo[:6])
            codigos.add(producto_codigo[1])

        for producto in resultados_nombre:
            if producto[1] not in codigos:
                self.tree.insert("", tk.END, values=producto[:6])

        if not producto_codigo and not resultados_nombre:
            messagebox.showinfo("Resultado", "No se encontraron productos.")

    def buscar_por_categoria(self):
        categoria = self.combo_busqueda_categoria.get().strip()
        if not categoria:
            messagebox.showwarning("Advertencia", "Seleccione una categoría.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = self.inventario.consultar_por_categoria(categoria)

        if productos:
            for producto in productos:
                self.tree.insert("", tk.END, values=producto[:6])
        else:
            messagebox.showinfo("Resultado", "No se encontraron productos en esa categoría.")

    def cargar_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = self.inventario.listar_productos()
        for producto in productos:
            self.tree.insert("", tk.END, values=producto[:6])

    def cargar_producto_en_formulario(self, producto):
        self.limpiar_campos()

        self.entry_codigo.config(state="normal")
        self.entry_codigo.insert(0, producto[1])
        self.entry_codigo.config(state="disabled")

        self.entry_nombre.insert(0, producto[2])
        self.combo_categoria.set(producto[3])
        self.entry_precio.insert(0, producto[4])
        self.entry_cantidad.insert(0, producto[5])
        self.text_descripcion.insert("1.0", producto[6] if producto[6] else "")
        self.text_caracteristicas.insert("1.0", producto[7] if producto[7] else "")

        self.ruta_imagen = producto[8] if len(producto) > 8 and producto[8] else ""
        self.label_imagen_ruta.config(text=os.path.basename(self.ruta_imagen) if self.ruta_imagen else "Sin imagen")

        if self.ruta_imagen and os.path.exists(self.ruta_imagen):
            self.mostrar_imagen(self.ruta_imagen)
        else:
            self.canvas_preview.delete("all")
            self.canvas_preview.create_text(
                self.preview_width // 2,
                self.preview_height // 2,
                text="Vista previa"
            )
            self.thumbnail = None

        self.modo_edicion = True

    def seleccionar_producto(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        item = self.tree.item(seleccion[0])
        valores = item["values"]
        if not valores:
            return

        codigo = valores[1]
        producto = self.inventario.consultar_por_codigo(codigo)

        if producto:
            self.cargar_producto_en_formulario(producto)

    def limpiar_campos(self):
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_cantidad.delete(0, tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.text_caracteristicas.delete("1.0", tk.END)

        self.ruta_imagen = ""
        self.label_imagen_ruta.config(text="Sin imagen")

        self.canvas_preview.delete("all")
        self.canvas_preview.create_text(
            self.preview_width // 2,
            self.preview_height // 2,
            text="Vista previa"
        )

        self.thumbnail = None
        self.modo_edicion = False

        categorias = self.inventario.obtener_categorias()
        if categorias:
            self.combo_categoria.set(categorias[0])