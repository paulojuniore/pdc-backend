# coding: utf-8
import sys

sys.path.append("./connection")
from Connection import Connection

# credenciais de conexão
conexao = Connection('localhost', 'bd-painel-de-controle', 'postgres', 'docker')

# consulta teste de conexão ao banco de dados
sql = 'SELECT * FROM "Discente" ORDER BY "ano_nascimento" LIMIT 10'
results = conexao.consultar(sql)

# imprimindo resultados da consulta
for line in results:
  print line

# fechar conexão
conexao.fechar()

