from flask import Flask, render_template, request, redirect, url_for
usuarios = []
app = Flask(__name__)

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

@app.route("/detalles")
def detalles():
    return render_template("detalles.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nuevo = {
            "nombre": request.form["nombre"],
            "correo": request.form["correo"],
            "contrasena": request.form["contrasena"]
        }
        usuarios.append(nuevo)
        return redirect(url_for("inicio"))
    return render_template("registro.html")

@app.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    contrasena = request.form["contrasena"]
    usuario = next((u for u in usuarios if u["correo"] == correo and u["contrasena"] == contrasena), None)
    if usuario:
        return redirect(url_for("inicio"))  # login exitoso
    return render_template("perfil.html", error="Correo o contraseña incorrectos")


if __name__ == "__main__":
    app.run(debug=True)