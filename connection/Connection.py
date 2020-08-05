# coding: utf-8
import psycopg2

# Classe que modulariza a conexão ao banco de dados postgres
class Connection(object):
  _db=None
  def __init__(self, mhost, database, user, password):
    self._db = psycopg2.connect(host=mhost, database=database, user=user, password=password)

  # Função para manipulação do banco, caso sejam necessárias inserções
  def manipular(self, sql):
    try:
      cursor = self._db.cursor()
      cursor.execute(sql)
      cursor.close()
      self._db.commit()
    except:
      return False
    return True

  # Função para queries SQL
  def consultar(self, sql):
    result=None
    try:
      cursor = self._db.cursor()
      cursor.execute(sql)
      result = cursor.fetchall()
    except:
      return None
    return result

  # Encerrar conexão com o banco de dados
  def fechar(self):
    self._db.close()

