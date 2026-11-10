# 🏢 Portal de Funcionários — Laboratório de Segurança Web (Build-and-Break)

> ⚠️ **APLICAÇÃO VULNERÁVEL DE PROPÓSITO.** Este projeto contém falhas de segurança plantadas intencionalmente, para fins **educacionais**. **Não hospede na internet.** Rode apenas em ambiente local / laboratório isolado. Todos os dados são **100% fictícios** (gerados com a biblioteca Faker).

Projeto de portfólio em **cibersegurança** que demonstra o ciclo completo de segurança de aplicação web: **construir uma aplicação vulnerável → atacá-la → corrigir as falhas**. O objetivo é mostrar, na prática, como vulnerabilidades clássicas surgem no código, como são exploradas e como se defendem.

---

## 🎯 Metodologia: Build-and-Break

A abordagem **build-and-break** (construir e quebrar) é uma forma de aprender segurança pelo lado de dentro: em vez de só ler sobre uma falha, você a **implementa de propósito**, **ataca** e depois **conserta**. Isso cria entendimento dos dois lados — do atacante (red team) e do defensor (blue team).

O projeto segue 4 fases:

| Fase | Nome | O que é | Status |
|------|------|---------|--------|
| 1 | **Construir** | Desenvolver o app com 3 falhas plantadas | ✅ Concluída |
| 2 | **Quebrar** | Explorar as falhas com ferramentas de pentest (sqlmap, hashcat) | 🔄 Em andamento |
| 3 | **Corrigir** | Reescrever o código fechando cada falha | ✅ Concluída |
| 4 | **Documentar** | Registrar os ataques e defesas em cenários reais | 🔄 Em andamento |

---

## 🧰 Stack

- **Python 3** + **Flask** — o portal web
- **MySQL** — banco de dados
- **Faker** (pt_BR) — geração de dados fictícios
- Ferramentas de ataque: **sqlmap**, **hashcat** / **John the Ripper**

---

## 📁 Estrutura do repositório

```
.
├── app-vulneravel/      # Versão com as falhas abertas (para estudo/ataque)
│   ├── app.py
│   └── seed.py
├── app-corrigido/       # Versão com todas as falhas fechadas
│   ├── app.py
│   └── seed.py
└── README.md
```

A existência das **duas versões** lado a lado é proposital: permite comparar diretamente o código vulnerável com o código seguro.

---

## 🐞 As 3 falhas plantadas

### 1. SQL Injection (no login)
A query de login é montada **concatenando** a entrada do usuário diretamente no texto SQL:

```python
# VULNERÁVEL
query = "SELECT * FROM funcionarios WHERE usuario = '" + usuario + "' AND senha_md5 = '" + md5(senha) + "'"
```

Como o valor digitado vira parte do comando SQL, é possível reescrever a lógica da consulta. Exemplo de **bypass de autenticação** no campo usuário:

```
' OR '1'='1' -- 
```

Isso comenta a verificação de senha e retorna o primeiro usuário da tabela, logando sem credencial válida.

### 2. Reflected XSS (na busca de colega)
O parâmetro de busca `q` é devolvido na página **sem nenhum tratamento**:

```python
# VULNERÁVEL
conteudo = f'<p>Você buscou por: {q}</p>'
```

Um atacante pode injetar HTML/JavaScript que será executado no navegador da vítima. Exemplo:

```
<script>alert('XSS')</script>
```

### 3. IDOR — Insecure Direct Object Reference (na ficha de funcionário)
A rota `/funcionario/<id>` exibe a ficha de **qualquer** funcionário (incluindo salário e CPF) **sem verificar** se o usuário logado tem permissão para vê-la:

```python
# VULNERÁVEL
cur.execute("SELECT * FROM funcionarios WHERE id = %s", (fid,))
```

Basta um usuário comum trocar o número na URL (`/funcionario/1`, `/funcionario/2`...) para acessar dados sensíveis de colegas.

---

## 🔒 As correções (Fase 3)

A versão em `app-corrigido/` fecha cada falha com a defesa adequada:

| Falha | Correção aplicada |
|-------|-------------------|
| SQL Injection | **Query parametrizada** — a entrada é passada como dado (`%s`), nunca concatenada no SQL |
| Reflected XSS | **Escape da saída** (`markupsafe.escape`) em tudo que é renderizado no HTML |
| IDOR | **Autorização por objeto** — salário e CPF só aparecem para o dono da ficha ou para papéis autorizados (RH/Admin) |
| Hash fraco (bônus) | Senhas migradas de **MD5** para **bcrypt** (com salt) |
| Extras | `debug=False` e `SECRET_KEY` forte via variável de ambiente |

---

## ▶️ Como rodar (ambiente local)

### Pré-requisitos
- Python 3 e MySQL instalados
- Dependências:

```bash
pip install flask mysql-connector-python faker bcrypt
```

### Banco de dados
Crie o banco e o usuário no MySQL:

```sql
CREATE DATABASE portal;
CREATE USER 'portal'@'localhost' IDENTIFIED BY 'portal123';
GRANT ALL PRIVILEGES ON portal.* TO 'portal'@'localhost';
```

### Rodar
```bash
# escolha a pasta: app-vulneravel ou app-corrigido
cd app-vulneravel
python seed.py     # popula o banco com dados fictícios
python app.py      # sobe o portal em http://localhost:5000
```

**Logins de teste:** `admin` / `admin123` · demais funcionários / `senha123`

---

## ⚔️ Fase 2 — Ataque (em andamento)

Exploração automatizada das falhas em ambiente de laboratório isolado.

**SQL Injection com sqlmap** (contra a versão vulnerável):
```bash
sqlmap -u "http://<IP-DO-LAB>:5000/" --data="usuario=admin&senha=123" -p usuario --batch --level=5 --risk=3 --dbs
```

**Quebra de hashes MD5** (após o dump da tabela):
```bash
hashcat -m 0 -a 0 hashes.txt rockyou.txt
```

> 📝 _Resultados reais do ataque (bancos listados, dump da tabela, hashes quebrados) serão documentados aqui em cenários narrativos — ex.: "atacante mira a gerente de RH para obter salário e CPF" — assim que a captura for concluída._

---

## 🧪 Disclaimer legal e ético

Este software foi criado **exclusivamente** para estudo de segurança em ambiente controlado. As técnicas aqui demonstradas só devem ser usadas contra sistemas próprios ou com **autorização explícita por escrito**. Atacar sistemas de terceiros sem consentimento é **crime**. O autor não se responsabiliza por uso indevido.

---

_Projeto de estudo em segurança de aplicações web._