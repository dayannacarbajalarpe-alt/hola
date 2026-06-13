from flask import Flask, render_template, request, redirect, url_for,abort,session
usuarios = []
app = Flask(__name__)
app.secret_key = "clave_secreta_12345"
productos=[
  {"id":1, "nombre": "Jean slim azul", "categoria": "jeans", "precio": 89.00 },
  {"id":2, "nombre": "Jean recto negro", "categoria": "jeans", "precio": 99.00 },
  {"id":3, "nombre": "Zapatillas urbanas", "categoria": "zapatos", "precio": 159.00 },
  {"id":4, "nombre": "Botines cuero", "categoria": "zapatos", "precio": 229.00 },
  {"id":5, "nombre": "Polo básico blanco", "categoria": "polos", "precio": 39.00 },
  {"id":6, "nombre": "Polo oversize gris", "categoria": "polos", "precio": 49.00 },
  {"id":7, "nombre": "Casaca denim", "categoria": "casacas", "precio": 179.50 },
  {"id":8, "nombre": "Casaca bomber", "categoria": "casacas", "precio": 199.00 }
]
@app.route("/")
def inicio():
    return render_template("index.html")
    
@app.route("/tienda")
def tienda():                
    return render_template("tienda.html")
    

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/carrito")
def carrito():
    return render_template("carrito.html")

@app.route("/detalles/<int:id>")
def detalles(id):
    producto = next((p for p in productos if p["id"] == id), None)
    if producto is None:
        abort(404)
    return render_template("detalles.html", producto=producto)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        correo = request.form["correo"]

        if any(u["correo"] == correo for u in usuarios):
            return render_template("registro.html", error="Este correo ya está registrado")

        nuevo = {
            "nombre": request.form["nombre"],
            "correo": correo,
            "contrasena": request.form["contrasena"]
        }
        usuarios.append(nuevo)
        return redirect(url_for("perfil"))
    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]
        usuario = next((u for u in usuarios if u["correo"] == correo and u["contrasena"] == contrasena), None)

        if usuario:
            session["usuario"] = usuario["nombre"]
            session["correo"] = usuario["correo"]
            return redirect(url_for("inicio"))

        return render_template("perfil.html", error="Usuario no encontrado")

    return render_template("perfil.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/mi-cuenta")
def mi_cuenta():
    if "usuario" not in session:
        return redirect(url_for("perfil"))
    return render_template("mi_cuenta.html", nombre=session["usuario"], correo=session["correo"])

if __name__ == "__main__":
    app.run(debug=True)

