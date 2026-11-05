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