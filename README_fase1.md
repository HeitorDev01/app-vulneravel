# 🔓 App Vulnerável — Fase 1 (Build & Break)

> ⚠️ **Aviso:** esta aplicação é **vulnerável de propósito**, só para fins de estudo.
> Não hospede na internet. Rode apenas localmente (`localhost`).

Projeto de portfólio em cibersegurança seguindo o ciclo **construir → quebrar → corrigir**.
Nesta Fase 1, construí um app web simples com **3 falhas clássicas** plantadas de propósito, pra aprender na prática como elas funcionam.

---

## 🧩 O que é

Um app de "notas" com login, onde cada usuário tem suas anotações. Simples de propósito — o foco são as falhas, não o visual.

**Stack:** Python + Flask + SQLite.

---

## ▶️ Como rodar

```bash
pip install flask
python app.py
```
Depois abra no navegador: `http://localhost:5000`

**Usuários de teste:**
- `heitor` / `senha123`
- `admin` / `sup3rs3cr3t`

---

## 🐞 As 3 falhas

### 1. SQL Injection (no login)
**O que é:** o código monta o comando do banco de dados juntando (concatenando) o que o usuário digita. Assim, o texto digitado vira **parte do comando**.

**Como testar:** no campo de usuário, digite:
```
' OR '1'='1' -- 
```
(com um espaço depois do `--`). Você entra **sem saber a senha**.

**Por que acontece:** o app mistura **dado** (o que você digita) com **comando** (o SQL). O `OR '1'='1'` é sempre verdadeiro e o `--` apaga o resto da verificação.

**Correção (Fase 3):** usar *queries parametrizadas* (o dado nunca vira comando).

---

### 2. XSS — Cross-Site Scripting
**O que é:** o site mostra o que o usuário digita direto na tela, sem tratar. Se o texto tiver código, o navegador **executa** esse código.

**Como testar (refletido, na busca):**
```
<script>alert('invadido')</script>
```
Aparece um pop-up. Isso prova que o site rodou um código que você injetou (num site seguro, apareceria só o texto).

**Como testar (armazenado, nas notas):** salve uma nota com o mesmo `<script>`. Agora o código roda **toda vez** que alguém abre o painel — é mais perigoso porque fica salvo.

**Por que acontece:** o app joga o texto no HTML sem "neutralizar" as tags. O navegador não distingue o texto normal do código do atacante.

**Correção (Fase 3):** tratar a saída (escapar o HTML) antes de mostrar.

---

### 3. IDOR — Insecure Direct Object Reference
**O que é:** o site mostra um recurso pelo número do ID na URL, **sem conferir se ele é seu**.

**Como testar:** logado como `heitor` (dono da nota #1), troque a URL para:
```
http://localhost:5000/nota/2
```
Você vê a nota do **admin**, que não é sua.

**Por que acontece:** o app confia no número da URL e não verifica o dono do recurso. Trocar o número dá acesso ao dado do vizinho.

**Correção (Fase 3):** checar se o recurso pertence ao usuário logado antes de mostrar.

---

## 🗺️ Próximas fases

- **Fase 2 — Quebrar:** atacar com ferramentas reais (sqlmap, Burp Suite) e extrair dados.
- **Fase 3 — Corrigir:** a versão segura de cada falha, lado a lado.
- **Fase 4 — Documentar:** mapear tudo no OWASP Top 10.

---

## 👤 Autor

**Heitor Carvalho** — [GitHub](https://github.com/HeitorDev01)