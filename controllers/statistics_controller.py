# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify, request
from . import routes
from util import constants

connection = Connection()

# Rota responsável por retornar o número de alunos evadidos do curso de Computação agrupados
#por período, onde o id_motivo deve ser um valor entre 1 e 9, inclusive.
@routes.route("/evadidos/<int:id_motivo>")
def escaped_from_periodo(id_motivo):
  if id_motivo >= 1 and id_motivo <= 9:
    query = 'SELECT semestre_vinculo, count(*) AS qtd_evadidos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
      ' AND id_situacao_vinculo=' + str(id_motivo) + '\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'
    result = connection.select(query)

    response = []
    for i in range(len(result)):
      response.append({ "semestre_vinculo": result[i][0], "qtd_evadidos": result[i][1] })

    return jsonify(response)
  else:
    return { "error": "Invalid resource" }

# Rota responsável por retornar o número de alunos egressos (formados) do curso de 
#Computação agrupados por período.
@routes.route("/egressos")
def graduates_by_period():
  query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
    ' AND id_situacao_vinculo=' + str(constants.GRADUADO) + '\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'
  result = connection.select(query)

  response = []
  for i in range(len(result)):
    response.append({ "semestre_vinculo": result[i][0], "qtd_egressos": result[i][1] })

  return jsonify(response)

@routes.route("/egressos/<minimo>/<maximo>")
def graduates_by_interval_of_periods(maximo, minimo):
  query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
    ' AND id_situacao_vinculo=' + str(constants.GRADUADO) + '\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'
  result = connection.select(query)
  
  min_index = 0
  max_index = 0
  for i in range(len(result)):
    if (result[i][0] == minimo):
      min_index = i
    elif (result[i][0] == maximo):
      max_index = i

  result_splitted = result[min_index:max_index+1]

  print (result_splitted)

  return { "min_index": min_index, "max_index": max_index }
