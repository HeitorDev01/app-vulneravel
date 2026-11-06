import mysql.connector, bcrypt
from faker import Faker
 
fake = Faker("pt_BR")
con = mysql.connector.connect(host="localhost", user="portal", password="portal123", database="portal")
cur = con.cursor()
 
cur.execute("DROP TABLE IF EXISTS funcionarios")
# CORRIGIDO: coluna renomeada p/ senha_hash e alargada p/ 60 chars (tamanho do bcrypt).
cur.execute("""
CREATE TABLE funcionarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100), email VARCHAR(100), cargo VARCHAR(100),
  salario DECIMAL(10,2), cpf VARCHAR(14),
  usuario VARCHAR(50), senha_hash VARCHAR(60)
)
""")

# CORRIGIDO: bcrypt com salt em vez de MD5. Cada hash é único mesmo p/ senhas iguais.
def hash_senha(s):
    return bcrypt.hashpw(s.encode(), bcrypt.gensalt()).decode()
 
# admin
cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_hash) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    ("Administrador", "admin@empresa.com", "TI - Admin", 15000, "000.000.000-00", "admin", hash_senha("admin123")))
 
# Maria Souza, do RH (papel que enxerga ficha de todos — usado no cenário do README)
cur.execute("INSERT INTO funcionarios (nome,email,cargo,salario,cpf,usuario,senha_hash) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    ("Maria Souza", "maria.souza@empresa.com", "RH - Gerente", 11000, fake.cpf(), "maria", hash_senha("senha123")))