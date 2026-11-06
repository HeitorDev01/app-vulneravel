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