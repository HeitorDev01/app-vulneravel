from flask import Flask, request, session, redirect, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-insegura-123"   # fraco de propósito

def init_db():
    con = sqlite3.connect("banco.db")
    con.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)")
    if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        con.execute("INSERT INTO usuarios (usuario, senha) VALUES ('heitor', 'senha123')")
        con.execute("INSERT INTO usuarios (usuario, senha) VALUES ('admin', 'sup3rs3cr3t')")
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
        con = sqlite3.connect("banco.db")
        # VULNERÁVEL: query montada concatenando texto do usuário
        query = "SELECT * FROM usuarios WHERE usuario = '" + usuario + "' AND senha = '" + senha + "'"
        print("Query executada:", query)
        resultado = con.execute(query).fetchone()
        con.close()
        if resultado:
            session["usuario"] = resultado[1]
            return redirect("/painel")
        erro = "Usuário ou senha inválidos"
    return render_template_string(PAGINA_LOGIN, erro=erro)

@app.route("/painel")