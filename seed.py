from flask import Flask, request, session, redirect, render_template_string
import mysql.connector, hashlib

app = Flask(__name__)
app.secret_key = "chave-insegura-123"

def db():
    return mysql.connector.connect(host="localhost", user="portal",
                                   password="portal123", database="portal")


def md5(s): return hashlib.md5(s.encode()).hexdigest()

PAGINA_LOGIN = """
<h2>Portal de Funcionários — Login</h2>
<form method="post">
  Usuário: <input name="usuario"><br><br>
  Senha: <input name="senha" type="password"><br><br>
  <button>Entrar</button>
</form>
<p style="color:red">{{ erro }}</p>
"""

@app.route("/", methods=["GET", "POST"])