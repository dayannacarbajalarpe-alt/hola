from flask import Flask, render_template, request, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
app = Flask(__name__)
app.secret_key = "clave_secreta_12345"
import os

database_url = os.environ.get('DATABASE_URL', 'sqlite:///usuarios.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)
import os
from werkzeug.utils import secure_filename
from datetime import datetime

class Pedido(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    nombre_producto = db.Column(db.String(100))
    precio      = db.Column(db.Float)
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)

app.config['UPLOAD_FOLDER'] = 'static/img'
class Usuario(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(100), nullable=False)
    correo     = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    es_admin   = db.Column(db.Boolean, default=False)

class Producto(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio    = db.Column(db.Float, nullable=False)
    imagen    = db.Column(db.String(200), default="default.jpg")

with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(correo="dayannacarbajalarpe@gmail.com").first():
        admin = Usuario(
            nombre     = "day",
            correo     = "dayannacarbajalarpe@gmail.com",
            contrasena = generate_password_hash("12345"),
            es_admin   = True
        )
        db.session.add(admin)

    if Producto.query.count() == 0:
        iniciales = [
            Producto(nombre="Jean slim azul",     categoria="jeans",   precio=89.00 ,imagen="jeans2.jpg"),
            Producto(nombre="Jean recto negro",   categoria="jeans",   precio=99.00 ,imagen="jeans2.jpg" ),
            Producto(nombre="Zapatillas urbanas", categoria="zapatos", precio=159.00 ,imagen="rojo.jpg" ),
            Producto(nombre="Botines cuero",      categoria="zapatos", precio=229.00 ,imagen="rojo.jpg"),
            Producto(nombre="Polo básico blanco", categoria="polos",   precio=39.00 ,imagen="rojo.jpg"),
            Producto(nombre="Polo oversize gris", categoria="polos",   precio=49.00 ,imagen="rojo.jpg"),
            Producto(nombre="Casaca denim",       categoria="casacas", precio=179.50 ,imagen="rojo.jpg"),
            Producto(nombre="Casaca bomber",      categoria="casacas", precio=199.00 ,imagen="casaca.jpg"),
        ]
        db.session.add_all(iniciales)

    db.session.commit()

@app.route("/")
def inicio():
    productos = Producto.query.all()
    return render_template("index.html", productos=productos)

@app.route("/tienda")
def tienda():
    productos = Producto.query.all()
    productos_json = json.dumps([
        {
            "id": p.id,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "precio": p.precio,
            "imagen": p.imagen
        }
        for p in productos
    ])
    return render_template("tienda.html", productos_json=productos_json)

@app.route("/carrito")
def carrito():
    if "usuario_id" not in session:
        return render_template("carrito.html", necesita_login=True)

    items = session.get("carrito", [])
    comprado = request.args.get("comprado")
    return render_template("carrito.html", carrito=items, comprado=comprado, necesita_login=False)

@app.route("/detalles/<int:id>")
def detalles(id):
    producto = Producto.query.get_or_404(id)
    return render_template("detalles.html", producto=producto)

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if request.method == "POST":
        correo     = request.form["correo"]
        contrasena = request.form["contrasena"]
        usuario    = Usuario.query.filter_by(correo=correo).first()

        if usuario and check_password_hash(usuario.contrasena, contrasena):
            session["usuario"]    = usuario.nombre
            session["correo"]     = usuario.correo
            session["usuario_id"] = usuario.id
            session["es_admin"]   = usuario.es_admin 
            return redirect(url_for("inicio"))

        return render_template("perfil.html", error="Correo o contraseña incorrectos")

    return render_template("perfil.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        correo = request.form["correo"]
        if Usuario.query.filter_by(correo=correo).first():
            return render_template("registro.html", error="Este correo ya está registrado")

        nuevo = Usuario(
            nombre     = request.form["nombre"],
            correo     = correo,
            contrasena = generate_password_hash(request.form["contrasena"])
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("perfil"))

    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/mi-cuenta")
def mi_cuenta():
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))
    usuario = Usuario.query.get(session["usuario_id"])
    return render_template("mi_cuenta.html", usuario=usuario)

@app.route("/editar-cuenta", methods=["GET", "POST"])
def editar_cuenta():
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))
    usuario = Usuario.query.get(session["usuario_id"])
    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.correo = request.form["correo"]
        nueva_contra   = request.form["contrasena"]
        if nueva_contra:
            usuario.contrasena = generate_password_hash(nueva_contra)
        db.session.commit()
        session["usuario"] = usuario.nombre
        session["correo"]  = usuario.correo
        return redirect(url_for("mi_cuenta"))
    return render_template("editar_cuenta.html", usuario=usuario)

@app.route("/eliminar-cuenta", methods=["POST"])
def eliminar_cuenta():
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))
    usuario = Usuario.query.get(session["usuario_id"])
    db.session.delete(usuario)
    db.session.commit()
    session.clear()
    return redirect(url_for("inicio"))

def solo_admin():
    return session.get("es_admin") == True

@app.route("/admin")
def admin():
    if not solo_admin():
        abort(403)
    productos = Producto.query.all()
    return render_template("admin.html", productos=productos)

@app.route("/admin/agregar", methods=["GET", "POST"])
def admin_agregar():
    if not solo_admin():
        abort(403)
    if request.method == "POST":
        archivo = request.files.get("imagen")
        nombre_imagen = "default.jpg"

        if archivo and archivo.filename:
            nombre_imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))

        nuevo = Producto(
            nombre    = request.form["nombre"],
            categoria = request.form["categoria"],
            precio    = float(request.form["precio"]),
            imagen    = nombre_imagen
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("admin_form.html", producto=None)

@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
def admin_editar(id):
    if not solo_admin():
        abort(403)
    producto = Producto.query.get_or_404(id)
    if request.method == "POST":
        producto.nombre    = request.form["nombre"]
        producto.categoria = request.form["categoria"]
        producto.precio    = float(request.form["precio"])

        archivo = request.files.get("imagen")
        if archivo and archivo.filename:
            nombre_imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))
            producto.imagen = nombre_imagen

        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("admin_form.html", producto=producto)

@app.route("/admin/borrar/<int:id>", methods=["POST"])
def admin_borrar(id):
    if not solo_admin():
        abort(403)
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/agregar-carrito/<int:id>")
def agregar_carrito(id):
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))

    producto = Producto.query.get_or_404(id)

    if "carrito" not in session:
        session["carrito"] = []

    carrito = session["carrito"]

    if not any(item["id"] == id for item in carrito):
        carrito.append({
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "imagen": producto.imagen
        })

    session["carrito"] = carrito
    return redirect(url_for("carrito"))

@app.route("/quitar-carrito/<int:id>")
def quitar_carrito(id):
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))

    if "carrito" in session:
        session["carrito"] = [item for item in session["carrito"] if item["id"] != id]

    return redirect(url_for("carrito"))
@app.route("/comprar", methods=["POST"])
def comprar():
    if "usuario_id" not in session:
        return redirect(url_for("perfil"))

    carrito = session.get("carrito", [])

    for item in carrito:
        pedido = Pedido(
            usuario_id = session["usuario_id"],
            producto_id = item["id"],
            nombre_producto = item["nombre"],
            precio = item["precio"]
        )
        db.session.add(pedido)

    db.session.commit()
    session["carrito"] = []
    return redirect(url_for("carrito", comprado=1))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not solo_admin():
        abort(403)

    total_productos = Producto.query.count()
    total_usuarios  = Usuario.query.count()
    total_pedidos   = Pedido.query.count()
    ingresos_totales = db.session.query(db.func.sum(Pedido.precio)).scalar() or 0

    # Ventas por categoría (join Pedido -> Producto)
    ventas_categoria = db.session.query(
        Producto.categoria, db.func.count(Pedido.id)
    ).join(Pedido, Pedido.producto_id == Producto.id).group_by(Producto.categoria).all()

    # Productos más vendidos
    mas_vendidos = db.session.query(
        Pedido.nombre_producto, db.func.count(Pedido.id).label("cantidad")
    ).group_by(Pedido.nombre_producto).order_by(db.func.count(Pedido.id).desc()).limit(5).all()

    datos = {
        "total_productos": total_productos,
        "total_usuarios": total_usuarios,
        "total_pedidos": total_pedidos,
        "ingresos_totales": round(ingresos_totales, 2),
        "categorias": [c[0] for c in ventas_categoria],
        "ventas_por_categoria": [c[1] for c in ventas_categoria],
        "productos_top": [p[0] for p in mas_vendidos],
        "cantidades_top": [p[1] for p in mas_vendidos],
    }

    return render_template("admin_dashboard.html", datos=datos)

if __name__ == "__main__":
    app.run(debug=True)