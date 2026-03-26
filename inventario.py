import sqlite3


class Producto:
    def __init__(self, codigo, nombre, categoria, precio, cantidad, descripcion="", caracteristicas="", imagen=""):
        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.categoria = categoria.strip()
        self.precio = precio
        self.cantidad = cantidad
        self.descripcion = descripcion.strip()
        self.caracteristicas = caracteristicas.strip()
        self.imagen = imagen.strip()
        self.validar()

    def validar(self):
        if not self.codigo:
            raise ValueError("El código no puede estar vacío.")
        if not self.nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if not self.categoria:
            raise ValueError("La categoría no puede estar vacía.")
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if self.cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "cantidad": self.cantidad,
            "descripcion": self.descripcion,
            "caracteristicas": self.caracteristicas,
            "imagen": self.imagen
        }


class Inventario:
    def __init__(self, db_name="tienda_esoterica.db"):
        self.db_name = db_name
        self.crear_tablas()
        self.migrar_base_si_es_necesario()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def crear_tablas(self):
        conexion = self.conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                precio REAL NOT NULL CHECK (precio >= 0),
                cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                descripcion TEXT,
                caracteristicas TEXT,
                imagen TEXT,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        """)

        conexion.commit()
        conexion.close()

    def migrar_base_si_es_necesario(self):
        conexion = self.conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
        existe_productos = cursor.fetchone()

        if not existe_productos:
            categorias_base = [
                "Velas rituales",
                "Inciensos",
                "Amuletos",
                "Minerales",
                "Libros espirituales",
                "Aceites esenciales"
            ]
            for categoria in categorias_base:
                cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (categoria,))
            conexion.commit()
            conexion.close()
            return

        cursor.execute("PRAGMA table_info(productos)")
        columnas = [col[1] for col in cursor.fetchall()]

        if "categoria_id" not in columnas:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos_nueva (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    categoria_id INTEGER NOT NULL,
                    precio REAL NOT NULL CHECK (precio >= 0),
                    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                    descripcion TEXT,
                    caracteristicas TEXT,
                    imagen TEXT,
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
                )
            """)

            if "categoria" in columnas:
                cursor.execute("SELECT DISTINCT categoria FROM productos")
                categorias_antiguas = cursor.fetchall()

                for cat in categorias_antiguas:
                    if cat[0]:
                        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (cat[0],))

                cursor.execute("""
                    SELECT codigo, nombre, categoria, precio, cantidad, descripcion, caracteristicas
                    FROM productos
                """)
                productos_antiguos = cursor.fetchall()

                for producto in productos_antiguos:
                    codigo, nombre, categoria, precio, cantidad, descripcion, caracteristicas = producto
                    cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria,))
                    categoria_row = cursor.fetchone()

                    if categoria_row:
                        categoria_id = categoria_row[0]
                        cursor.execute("""
                            INSERT OR IGNORE INTO productos_nueva
                            (codigo, nombre, categoria_id, precio, cantidad, descripcion, caracteristicas, imagen)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo, nombre, categoria_id, precio, cantidad, descripcion, caracteristicas, ""
                        ))

                cursor.execute("DROP TABLE productos")
                cursor.execute("ALTER TABLE productos_nueva RENAME TO productos")

        categorias_base = [
            "Velas rituales",
            "Inciensos",
            "Amuletos",
            "Minerales",
            "Libros espirituales",
            "Aceites esenciales"
        ]

        for categoria in categorias_base:
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (categoria,))

        conexion.commit()
        conexion.close()

    def obtener_categorias(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        categorias = [fila[0] for fila in cursor.fetchall()]
        conexion.close()
        return categorias

    def agregar_categoria(self, nombre):
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre de la categoría no puede estar vacío."

        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
            conexion.commit()
            return True, "Categoría agregada correctamente."
        except sqlite3.IntegrityError:
            return False, "Esa categoría ya existe."
        finally:
            conexion.close()

    def contar_productos_por_categoria(self, nombre_categoria):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE LOWER(c.nombre) = LOWER(?)
        """, (nombre_categoria,))
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    def eliminar_categoria(self, nombre_categoria):
        nombre_categoria = nombre_categoria.strip()
        if not nombre_categoria:
            return False, "Debe indicar una categoría."

        total_productos = self.contar_productos_por_categoria(nombre_categoria)
        if total_productos > 0:
            return False, "No se puede eliminar la categoría porque tiene productos asociados."

        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM categorias
            WHERE LOWER(nombre) = LOWER(?)
        """, (nombre_categoria,))
        conexion.commit()
        filas_afectadas = cursor.rowcount
        conexion.close()

        if filas_afectadas > 0:
            return True, "Categoría eliminada correctamente."
        return False, "No se encontró la categoría."

    def obtener_categoria_id(self, nombre_categoria):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM categorias WHERE LOWER(nombre) = LOWER(?)", (nombre_categoria,))
        resultado = cursor.fetchone()
        conexion.close()
        return resultado[0] if resultado else None

    def agregar_producto(self, producto):
        datos = producto.to_dict()
        categoria_id = self.obtener_categoria_id(datos["categoria"])

        if categoria_id is None:
            return False, "La categoría no existe. Debe crearla primero."

        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                INSERT INTO productos (
                    codigo, nombre, categoria_id, precio, cantidad, descripcion, caracteristicas, imagen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos["codigo"],
                datos["nombre"],
                categoria_id,
                datos["precio"],
                datos["cantidad"],
                datos["descripcion"],
                datos["caracteristicas"],
                datos["imagen"]
            ))
            conexion.commit()
            return True, "Producto agregado correctamente."
        except sqlite3.IntegrityError:
            return False, "Ya existe un producto con ese código."
        finally:
            conexion.close()

    def listar_productos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.codigo, p.nombre, c.nombre, p.precio, p.cantidad, p.descripcion, p.caracteristicas, p.imagen
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nombre
        """)
        productos = cursor.fetchall()
        conexion.close()
        return productos

    def consultar_por_codigo(self, codigo):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.codigo, p.nombre, c.nombre, p.precio, p.cantidad, p.descripcion, p.caracteristicas, p.imagen
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.codigo = ?
        """, (codigo,))
        producto = cursor.fetchone()
        conexion.close()
        return producto

    def consultar_por_nombre(self, nombre):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.codigo, p.nombre, c.nombre, p.precio, p.cantidad, p.descripcion, p.caracteristicas, p.imagen
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE LOWER(p.nombre) LIKE LOWER(?)
            ORDER BY p.nombre
        """, (f"%{nombre}%",))
        productos = cursor.fetchall()
        conexion.close()
        return productos

    def consultar_por_categoria(self, categoria):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.codigo, p.nombre, c.nombre, p.precio, p.cantidad, p.descripcion, p.caracteristicas, p.imagen
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE LOWER(c.nombre) = LOWER(?)
            ORDER BY p.nombre
        """, (categoria,))
        productos = cursor.fetchall()
        conexion.close()
        return productos

    def eliminar_producto(self, codigo):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
        conexion.commit()
        filas_afectadas = cursor.rowcount
        conexion.close()

        if filas_afectadas > 0:
            return True, "Producto eliminado correctamente."
        return False, "No se encontró un producto con ese código."

    def modificar_producto(self, codigo, **kwargs):
        campos_actualizar = []
        valores = []

        if "categoria" in kwargs:
            categoria_id = self.obtener_categoria_id(kwargs["categoria"])
            if categoria_id is None:
                return False, "La categoría no existe."
            campos_actualizar.append("categoria_id = ?")
            valores.append(categoria_id)
            del kwargs["categoria"]

        campos_validos = {"nombre", "precio", "cantidad", "descripcion", "caracteristicas", "imagen"}

        for campo, valor in kwargs.items():
            if campo in campos_validos:
                if campo in ("precio", "cantidad") and valor < 0:
                    return False, f"El campo {campo} no puede ser negativo."
                campos_actualizar.append(f"{campo} = ?")
                valores.append(valor)

        if not campos_actualizar:
            return False, "No se enviaron campos válidos para actualizar."

        valores.append(codigo)

        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute(
            f"UPDATE productos SET {', '.join(campos_actualizar)} WHERE codigo = ?",
            tuple(valores)
        )
        conexion.commit()
        filas_afectadas = cursor.rowcount
        conexion.close()

        if filas_afectadas > 0:
            return True, "Producto modificado correctamente."
        return False, "No se encontró un producto con ese código."

    def registrar_venta(self, codigo, cantidad_vendida):
        if cantidad_vendida <= 0:
            return False, "La cantidad vendida debe ser mayor que cero."

        producto = self.consultar_por_codigo(codigo)
        if not producto:
            return False, "No se encontró el producto."

        stock_actual = producto[5]

        if cantidad_vendida > stock_actual:
            return False, "No hay suficiente inventario para realizar la venta."

        nuevo_stock = stock_actual - cantidad_vendida

        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos
            SET cantidad = ?
            WHERE codigo = ?
        """, (nuevo_stock, codigo))
        conexion.commit()
        conexion.close()

        return True, f"Venta registrada correctamente. Stock restante: {nuevo_stock}"