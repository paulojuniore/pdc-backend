# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from util import constants

class Curso():
  connection = None

  def __init__(self):
    # Instância da conexão ao banco de dados.
    self.connection = Connection()

  # Função que retorna informações sobre os alunos ativos do curso de Computação,
  ## informações estas que são a matrícula do aluno e a porcentagem concluída do 
  ### curso com base na quantidade de créditos que o aluno já possui.
  def get_actives(self):
    query = 'SELECT "DiscenteVinculo".matricula, SUM("Disciplina".creditos)\
      FROM "DiscenteVinculo"\
      INNER JOIN "DiscenteDisciplina"\
        ON "DiscenteVinculo".matricula="DiscenteDisciplina".matricula\
      INNER JOIN "Turma"\
        ON "DiscenteDisciplina".id_turma="Turma".id\
      INNER JOIN "Disciplina"\
        ON "Turma".id_disciplina="Disciplina".id\
      WHERE id_curso=' + str(constants.COMPUTACAO_ID)  + '\
      AND id_situacao_vinculo=' + str(constants.ATIVO) + '\
      AND "DiscenteDisciplina".id_situacao=' + str(constants.ID_APROVADO) + '\
      GROUP BY "DiscenteVinculo".matricula\
      ORDER BY SUM("Disciplina".creditos) DESC'

    result = self.connection.select(query)

    json_return = []
    for registro in result:
      percent = (registro[1] * 100) / int(constants.TOTAL_CREDITOS)
      periodo_ingresso = str(registro[0][1:3]) + "." + str(registro[0][3])
      json_return.append({ "matricula": registro[0], "periodo_ingresso": periodo_ingresso,
        "porcentagem_concluida": round(percent, 2) })

    return jsonify(json_return)