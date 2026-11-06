import mysql.connector, hashlib
from faker import Faker

fake = Faker("pt_BR")
con = mysql.connector.connect(host="localhost", user="portal", password="portal123", database="portal")
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS funcionarios")
cur.execute("""
CREATE TABLE funcionarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100), email VARCHAR(100), cargo VARCHAR(100),
  salario DECIMAL(10,2), cpf VARCHAR(14),
  usuario VARCHAR(50), senha_md5 VARCHAR(32)
)
""")

def md5(s): return hashlib.md5(s.encode()).hexdigest()

# admin
cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_md5) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    ("Administrador", "admin@empresa.com", "TI - Admin", 15000, "000.000.000-00", "admin", md5("admin123")))


# 20 funcionarios ficticios
for _ in range(20):
    nome = fake.name()
    usuario = nome.split()[0].lower() + str(fake.random_int(1, 99))
    cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_md5) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (nome, fake.email(), fake.job(), fake.random_int(2000, 12000), fake.cpf(), usuario, md5("senha123")))

con.commit()
con.close()
print("Banco populado!")