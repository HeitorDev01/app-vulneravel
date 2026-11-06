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
def login():
    erro = ""
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        con = db(); cur = con.cursor(dictionary=True)
        # VULNERÁVEL: SQL injection (usuário concatenado)
        query = "SELECT * FROM funcionarios WHERE usuario = '" + usuario + "' AND senha_md5 = '" + md5(senha) + "'"
        print("Query:", query)
        cur.execute(query)
        f = cur.fetchone()
        con.close()
        if f:
            session["id"] = f["id"]; session["nome"] = f["nome"]
            return redirect("/painel")
        erro = "Usuário ou senha inválidos"
    return render_template_string(PAGINA_LOGIN, erro=erro)

@app.route("/painel")
def painel():
    if "id" not in session: return redirect("/")
    con = db(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM funcionarios WHERE id = %s", (session["id"],))
    eu = cur.fetchone(); con.close()
    return f"""
    <h2>Bem-vindo, {eu['nome']}</h2>
    <h3>Meus dados</h3>
    <ul>
      <li>Cargo: {eu['cargo']}</li>
      <li>Salário: R$ {eu['salario']}</li>
      <li>CPF: {eu['cpf']}</li>
      <li>E-mail: {eu['email']}</li>
    </ul>
    <h3>Buscar colega</h3>
    <form method="get" action="/buscar">
      <input name="q" placeholder="nome do colega"><button>Buscar</button>
    </form>
    <p>Ver ficha por ID: <a href="/funcionario/2">/funcionario/2</a></p>
    <a href="/sair">Sair</a>
    """