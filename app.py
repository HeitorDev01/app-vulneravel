from flask import Flask, request, session, redirect, render_template_string
import mysql.connector, hashlib

app = Flask(__name__)
app.secret_key = "chave-insegura-123"

def db():
    return mysql.connector.connect(host="localhost", user="portal",
                                   password="portal123", database="portal")

def md5(s): return hashlib.md5(s.encode()).hexdigest()

def pagina(titulo, conteudo, logado=True):
    topo = '<a href="/sair" class="sair">Sair</a>' if logado else ''
    return f"""
<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} — Portal do Colaborador</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#eef1f5;color:#1f2a37}}
  header{{background:#13315c;color:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:center}}
  header h1{{font-size:18px;font-weight:600}}
  header .sair{{color:#cdd9ec;text-decoration:none;font-size:14px}}
  .container{{max-width:720px;margin:32px auto;padding:0 16px}}
  .card{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
  .card h2{{font-size:16px;margin-bottom:16px;color:#13315c}}
  label{{display:block;font-size:13px;color:#475569;margin-bottom:4px}}
  input{{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;font-size:14px;margin-bottom:14px}}
  button{{background:#13315c;color:#fff;border:0;padding:10px 18px;border-radius:8px;font-size:14px;cursor:pointer}}
  button:hover{{background:#1d4e89}}
  table{{width:100%;border-collapse:collapse}}
  td{{padding:8px 0;border-bottom:1px solid #eef1f5;font-size:14px}}
  td.rot{{color:#64748b;width:130px}}
  ul.lista{{list-style:none}}
  ul.lista li{{padding:10px 0;border-bottom:1px solid #eef1f5;font-size:14px}}
  a{{color:#1d4e89}}
  .erro{{color:#b91c1c;font-size:14px;margin-top:8px}}
</style></head><body>
<header><h1>🏢 Empresa XYZ — Portal do Colaborador</h1>{topo}</header>
<div class="container">{conteudo}</div>
</body></html>
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
        cur.execute(query); f = cur.fetchone(); con.close()
        if f:
            session["id"] = f["id"]; session["nome"] = f["nome"]
            return redirect("/painel")
        erro = "Usuário ou senha inválidos"
    conteudo = f"""
    <div class="card">
      <h2>Acesse sua conta</h2>
      <form method="post">
        <label>Usuário</label><input type="text" name="usuario">
        <label>Senha</label><input type="password" name="senha">
        <button>Entrar</button>
      </form>
      <div class="erro">{erro}</div>
    </div>"""
    return pagina("Login", conteudo, logado=False)

@app.route("/painel")
def painel():
    if "id" not in session: return redirect("/")
    con = db(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM funcionarios WHERE id = %s", (session["id"],))
    eu = cur.fetchone(); con.close()
    conteudo = f"""
    <div class="card">
      <h2>Meus dados</h2>
      <table>
        <tr><td class="rot">Nome</td><td>{eu['nome']}</td></tr>
        <tr><td class="rot">Cargo</td><td>{eu['cargo']}</td></tr>
        <tr><td class="rot">Salário</td><td>R$ {eu['salario']}</td></tr>
        <tr><td class="rot">CPF</td><td>{eu['cpf']}</td></tr>
        <tr><td class="rot">E-mail</td><td>{eu['email']}</td></tr>
      </table>
    </div>
    <div class="card">
      <h2>Buscar colega</h2>
      <form method="get" action="/buscar">
        <input type="text" name="q" placeholder="nome do colega">
        <button>Buscar</button>
      </form>
    </div>"""
    return pagina(f"Olá, {eu['nome']}", conteudo)

@app.route("/buscar")
def buscar():
    if "id" not in session: return redirect("/")
    q = request.args.get("q", "")
    con = db(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT id, nome, cargo FROM funcionarios WHERE nome LIKE %s", (f"%{q}%",))
    rows = cur.fetchall(); con.close()
    itens = "".join(f"<li><a href='/funcionario/{r['id']}'>{r['nome']}</a> — {r['cargo']}</li>" for r in rows)
    # VULNERÁVEL: reflected XSS (q sem tratamento)
    conteudo = f"""
    <div class="card">
      <h2>Resultados da busca</h2>
      <p style="color:#475569;font-size:14px;margin-bottom:12px">Você buscou por: {q}</p>
      <ul class="lista">{itens}</ul>
      <p style="margin-top:12px"><a href="/painel">← Voltar</a></p>
    </div>"""
    return pagina("Busca", conteudo)

@app.route("/funcionario/<int:fid>")
def funcionario(fid):
    if "id" not in session: return redirect("/")
    con = db(); cur = con.cursor(dictionary=True)
    # VULNERÁVEL: IDOR (mostra qualquer ficha, sem checar o dono)
    cur.execute("SELECT * FROM funcionarios WHERE id = %s", (fid,))
    f = cur.fetchone(); con.close()
    if not f: return pagina("Não encontrado", '<div class="card">Funcionário não encontrado. <a href="/painel">Voltar</a></div>')
    conteudo = f"""
    <div class="card">
      <h2>Ficha de {f['nome']}</h2>
      <table>
        <tr><td class="rot">Cargo</td><td>{f['cargo']}</td></tr>
        <tr><td class="rot">Salário</td><td>R$ {f['salario']}</td></tr>
        <tr><td class="rot">CPF</td><td>{f['cpf']}</td></tr>
        <tr><td class="rot">E-mail</td><td>{f['email']}</td></tr>
      </table>
      <p style="margin-top:12px"><a href="/painel">← Voltar</a></p>
    </div>"""
    return pagina(f"Ficha de {f['nome']}", conteudo)

@app.route("/sair")
def sair():
    session.clear(); return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)