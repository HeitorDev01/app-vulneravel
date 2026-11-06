from flask import Flask, request, session, redirect, render_template_string
import mysql.connector, hashlib

app = Flask(__name__)
app.secret_key = "chave-insegura-123"

def db():
    return mysql.connector.connect(host="localhost", user="portal",
                                   password="portal123", database="portal")


def md5(s): return hashlib.md5(s.encode()).hexdigest()

# admin
cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_md5) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    ("Administrador", "admin@empresa.com", "TI - Admin", 15000, "000.000.000-00", "admin", md5("admin123")))

# funcionarios fixos (dados escolhidos por você)
fixos = [
    ("Heitor Carvalho", 
     "heitor@empresa.com", 
     "Analista de TI", 
     6500, 
     "111.222.333-44", 
     "heitor", 
     md5("senha123")),
    ("Maria Souza", 
     "maria@empresa.com",
     "RH - Gerente", 
     9000, 
     "555.666.777-88", 
     "maria",
     md5("maria2024")),
]
for f in fixos:
    cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_md5) VALUES (%s,%s,%s,%s,%s,%s,%s)", f)

# 20 funcionarios ficticios
for _ in range(20):
    nome = fake.name()
    usuario = nome.split()[0].lower() + str(fake.random_int(1, 99))
    cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_md5) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (nome, fake.email(), fake.job(), fake.random_int(2000, 12000), fake.cpf(), usuario, md5("senha123")))

con.commit()
con.close()
print("Banco populado!")