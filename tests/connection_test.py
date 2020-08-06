# coding: utf-8
import sys
sys.path.append("../connection")
from Connection import Connection

# credenciais de conexão
connection = Connection('localhost', 'bd_development', 'postgres', 'docker')

# função para processar as queries para teste
def process_query(sql):
  return connection.select(sql)

# teste de resultado da consulta na tabela Genero
def test_result_of_table_genre():
  query = 'SELECT * FROM "Genero"'
  assert process_query(query) == [(1,'Feminino'), (2,'Masculino')]

# teste de número de registros na tabela Genero
def test_number_of_genres():
  query = 'SELECT * FROM "Genero"'
  assert len(process_query(query)) == 2

# teste da quantidade de registros na tabela Discente
def test_amount_of_records():
  query = 'SELECT * FROM "Discente"'
  assert len(process_query(query)) == 2144

# teste de query limitando aos 10 primeiros registros na tabela Discente
def test_limit_of_records():
  query = 'SELECT * FROM "Discente" LIMIT 10'
  assert len(process_query(query)) == 10