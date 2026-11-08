import os, secrets
from flask import Flask, request, session, redirect
from markupsafe import escape
import mysql.connector, bcrypt

app = Flask(__name__)
# CORRIGIDO: secret_key forte, vinda de variável de ambiente (nunca hardcoded).
# Em lab, se não houver a variável, gera uma aleatória por execução.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

def db():
    return mysql.connector.connect(host="localhost", user="portal",
                                   password="portal123", database="portal")

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
  .restrito{{color:#94a3b8;font-style:italic}}
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
        # CORRIGIDO (SQLi): query parametrizada. A entrada vai como DADO (%s),
        # nunca concatenada no texto do SQL, então ' OR '1'='1 deixa de funcionar.
        cur.execute("SELECT * FROM funcionarios WHERE usuario = %s", (usuario,))
        f = cur.fetchone(); con.close()
        # CORRIGIDO (hash fraco): verificação com bcrypt em vez de comparar MD5.
        if f and bcrypt.checkpw(senha.encode(), f["senha_hash"].encode()):
            session["id"] = f["id"]
            session["nome"] = f["nome"]
            session["cargo"] = f["cargo"]   # guardado p/ decidir autorização depois
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
        <tr><td class="rot">Nome</td><td>{escape(eu['nome'])}</td></tr>
        <tr><td class="rot">Cargo</td><td>{escape(eu['cargo'])}</td></tr>
        <tr><td class="rot">Salário</td><td>R$ {eu['salario']}</td></tr>
        <tr><td class="rot">CPF</td><td>{escape(eu['cpf'])}</td></tr>
        <tr><td class="rot">E-mail</td><td>{escape(eu['email'])}</td></tr>
      </table>
    </div>
    <div class="card">
      <h2>Buscar colega</h2>
      <form method="get" action="/buscar">
        <input type="text" name="q" placeholder="nome do colega">
        <button>Buscar</button>
      </form>
    </div>"""
    return pagina(f"Olá, {escape(eu['nome'])}", conteudo)

@app.route("/buscar")
def buscar():
    if "id" not in session: return redirect("/")
    q = request.args.get("q", "")
    con = db(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT id, nome, cargo FROM funcionarios WHERE nome LIKE %s", (f"%{q}%",))
    rows = cur.fetchall(); con.close()
    # CORRIGIDO (XSS): escape() em tudo que vai pro HTML — o que o usuário
    # digitou (q) e também os dados vindos do banco. Tags viram texto inofensivo.
    itens = "".join(
        f"<li><a href='/funcionario/{r['id']}'>{escape(r['nome'])}</a> — {escape(r['cargo'])}</li>"
        for r in rows
    )
    conteudo = f"""
    <div class="card">
      <h2>Resultados da busca</h2>
      <p style="color:#475569;font-size:14px;margin-bottom:12px">Você buscou por: {escape(q)}</p>
      <ul class="lista">{itens}</ul>
      <p style="margin-top:12px"><a href="/painel">← Voltar</a></p>
    </div>"""
    return pagina("Busca", conteudo)

def pode_ver_dados_sensiveis(fid):
    # Dono vê a própria ficha completa; RH e Admin podem ver de todos.
    if fid == session.get("id"):
        return True
    cargo = session.get("cargo", "")
    return cargo.startswith("RH") or "Admin" in cargo

@app.route("/funcionario/<int:fid>")
def funcionario(fid):
    if "id" not in session: return redirect("/")
    con = db(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM funcionarios WHERE id = %s", (fid,))
    f = cur.fetchone(); con.close()
    if not f:
        return pagina("Não encontrado", '<div class="card">Funcionário não encontrado. <a href="/painel">Voltar</a></div>')
    # CORRIGIDO (IDOR): autorização por objeto. Salário e CPF só aparecem
    # para o dono da ficha ou para quem tem papel autorizado (RH/Admin).
    completo = pode_ver_dados_sensiveis(fid)
    linhas = f"""
        <tr><td class="rot">Cargo</td><td>{escape(f['cargo'])}</td></tr>
        <tr><td class="rot">E-mail</td><td>{escape(f['email'])}</td></tr>"""
    if completo:
        linhas += f"""
        <tr><td class="rot">Salário</td><td>R$ {f['salario']}</td></tr>
        <tr><td class="rot">CPF</td><td>{escape(f['cpf'])}</td></tr>"""
    else:
        linhas += """
        <tr><td class="rot">Salário</td><td class="restrito">— restrito</td></tr>
        <tr><td class="rot">CPF</td><td class="restrito">— restrito</td></tr>"""
    conteudo = f"""
    <div class="card">
      <h2>Ficha de {escape(f['nome'])}</h2>
      <table>{linhas}</table>
      <p style="margin-top:12px"><a href="/painel">← Voltar</a></p>
    </div>"""
    return pagina(f"Ficha de {escape(f['nome'])}", conteudo)

@app.route("/sair")
def sair():
    session.clear(); return redirect("/")

if __name__ == "__main__"
    # CORRIGIDO: debug desligado — debug=True expõe o console interativo do Werkzeug.
    app.run(debug=False, host="127.0.0.1", port=5000)