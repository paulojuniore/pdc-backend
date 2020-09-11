# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from util import constants

class Curso():

  def __init__(self):
    # Instância da conexão ao banco de dados.
    self.connection = Connection()

  # Função que conta o número de períodos que o aluno está ativo no curso.
  def count_number_of_periods(self, ano_ingresso, semestre_ingresso):
    #Contador de  periodos ativos
    cpa = 0

    while ano_ingresso < int(constants.ANO_ATUAL):
      while semestre_ingresso <= 2:
        semestre_ingresso += 1
        cpa += 1
      semestre_ingresso = 1 
      ano_ingresso += 1

    # coletando a diferença quando AI == AA
    cpa += int(constants.SEMESTRE_ATUAL) - 1
    result = [0, False]

    # Caso seja fera
    if cpa == 0 or cpa > 14:
        result = [cpa, False]
    # Caso não seja fera
    elif (cpa >= 1):
        result = [cpa, True]

    return result

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
      # percentual do curso concluído, com base na quantidade de créditos cursados. 
      percentual_concluido = (registro[1] * 100) / int(constants.TOTAL_CREDITOS)

      ano_ingresso = registro[0][1:3]
      semestre_ingresso = registro[0][3]

      periodo_ingresso = ano_ingresso + "." + semestre_ingresso

      # retorna uma lista com dois elementos, onde o primeiro é o número de períodos
      ## que o aluno está ativo e o segundo é um boolean que indica se ele é fera (False)
      ### ou não (True)
      periodos_ativos = self.count_number_of_periods(int(ano_ingresso), int(semestre_ingresso))
      
      # o aluno ativo só é adicionado a resposta json se ele não é um fera, ou seja, não
      ## ingressou no período atual.
      if (periodos_ativos[1]):
        json_return.append({ "matricula": registro[0], "periodo_ingresso": periodo_ingresso,
          "porcentagem_concluida": round(percentual_concluido, 2), "periodos_ativos": periodos_ativos[0] })

    return jsonify(json_return)