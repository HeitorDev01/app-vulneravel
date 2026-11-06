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
    # VULNERÁVEL: stored XSS (texto da nota mostrado sem tratamento)
    itens = "".join(f"<li><a href='/nota/{n['id']}'>nota #{n['id']}</a>: {n['texto']}</li>" for n in notas)
    return f"""
    <h2>Bem-vindo, {session['usuario']}!</h2>
    <form method="get" action="/busca">
      <input name="q" placeholder="buscar nota"><button>Buscar</button>
    </form>
    <h3>Suas notas</h3>
    <ul>{itens}</ul>
    <form method="post">
      <input name="texto" placeholder="nova nota"><button>Adicionar</button>
    </form>
    <a href="/sair">Sair</a>
    """


@app.route("/busca")
def busca():
    if "usuario_id" not in session:
        return redirect("/")
    q = request.args.get("q", "")
    con = db()
    notas = con.execute("SELECT * FROM notas WHERE usuario_id = ? AND texto LIKE ?",
                        (session["usuario_id"], f"%{q}%")).fetchall()
    con.close()
    itens = "".join(f"<li>{n['texto']}</li>" for n in notas)
    # VULNERÁVEL: reflected XSS (o termo é devolvido sem tratamento)
    return f"""
    <h2>Resultados</h2>
    <p>Você buscou por: {q}</p>
    <ul>{itens}</ul>
    <a href="/painel">Voltar</a>
    """

@app.route("/nota/<int:nota_id>")
def nota(nota_id):
    if "usuario_id" not in session:
        return redirect("/")
    con = db()
    # VULNERÁVEL: IDOR (busca pelo id SEM conferir o dono)
    n = con.execute("SELECT * FROM notas WHERE id = ?", (nota_id,)).fetchone()
    con.close()
    if not n:
        return "Nota não encontrada"
    return f"<h2>Nota #{n['id']}</h2><p>{n['texto']}</p><a href='/painel'>Voltar</a>"

@app.route("/sair")
def sair():
        session.clear()
        return redirect("/")