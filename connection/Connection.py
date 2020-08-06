# coding: utf-8
import psycopg2

# Classe que modulariza a conexão ao banco de dados postgres
class Connection(object):
  _db=None

  # Construtor da Conexão ao bd.
  # hostname: localhost ou IP
  # database: nome do banco de dados
  # user: nome de usuário do banco de dados
  # password: senha do usuário de banco de dados
  def __init__(self, hostname, database, user, password):
    self._db = psycopg2.connect(host=hostname, database=database, user=user, password=password)

  # Função para manipulação do banco, caso sejam necessárias inserções, onde a query sql é
  #passada como parâmetro.
  # sql: Query a ser executa no banco de dados
  def manipulate(self, sql):
    try:
      cursor = self._db.cursor()
      cursor.execute(sql)
      cursor.close()
      self._db.commit()
    except:
      return False
    return True

  # Função para queries de consultas SQL.
  # sql: Query de consulta a ser executada no banco de dados.
  def select(self, sql):
    result=None
    try:
      cursor = self._db.cursor()
      cursor.execute(sql)
      result = cursor.fetchall()
    except:
      return None
    return result

  # Encerrar conexão com o banco de dados
  def close(self):
    self._db.close()

