# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from . import routes

connection = Connection()

@routes.route("/egressos")
def graduates_by_period():
  query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=4 AND id_situacao_vinculo=10\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'
  result = connection.select(query)

  response = []
  for i in range(len(result)):
    response.append({ "semestre_vinculo": result[i][0], "qtd_egressos": result[i][1] })

  return jsonify(response)
