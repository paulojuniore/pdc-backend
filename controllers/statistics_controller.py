# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from . import routes

from util import constants

connection = Connection()

@routes.route("/evadidos/<int:id_motivo>")
def escaped_from_periodo(id_motivo):
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
