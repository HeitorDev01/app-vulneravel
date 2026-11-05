from flask import Flask, request, session, redirect, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-insegura-123"

def db():
    con = sqlite3.connect("banco.db")
    con.row_factory = sqlite3.Row
    return con   # fraco de propósito

def init_db():
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS notas (id INTEGER PRIMARY KEY, usuario_id INTEGER, texto TEXT)")
    if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        con.execute("INSERT INTO usuarios (usuario, senha) VALUES ('heitor', 'senha123')")
        con.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 'sup3rs3cr3t')")
        con.execute("INSERT INTO notas (usuario_id, texto) VALUES (1, 'Comprar resistores')")
        con.execute("INSERT INTO notas (usuario_id, texto) VALUES (2, 'Senha do servidor: root/root')")
        con.commit()
    con.close()

PAGINA_LOGIN = """
<h2>Login</h2>
<form method="post">
  Usuário: <input name="usuario"><br><br>
  Senha: <input name="senha" type="password"><br><br>
  <button>Entrar</button>
</form>
<p style="color:red">{{ erro }}</p>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    erro = ""
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        con = db()
        # VULNERÁVEL: SQL injection (query concatenada)
        query = "SELECT * FROM usuarios WHERE usuario = '" + usuario + "' AND senha = '" + senha + "'"
        print("Query executada:", query)
        resultado = con.execute(query).fetchone()
        con.close()
        if resultado:
            session["usuario_id"] = resultado["id"]
            session["usuario"] = resultado["usuario"]
            return redirect("/painel")
        erro = "Usuário ou senha inválidos"
    return render_template_string(PAGINA_LOGIN, erro=erro)

@app.route("/painel", methods=["GET", "POST"])
def painel():
    if "usuario_id" not in session:
        return redirect("/")
    con = db()
    if request.method == "POST":
        con.execute("INSERT INTO notas (usuario_id, texto) VALUES (?, ?)",
                    (session["usuario_id"], request.form["texto"]))
        con.commit()
    notas = con.execute("SELECT * FROM notas WHERE usuario_id = ?",
                        (session["usuario_id"],)).fetchall()
    con.close()

@app.route("/sair")
def sair():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)