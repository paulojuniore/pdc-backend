# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify, request
from . import routes
from util import constants

connection = Connection()

# Função que retorna estatísticas sobre os egressos, informações como o total de graduados
## em um determinado intervalo de tempo, média de graduados, períodos que tiveram mais e menos
### graduados e seus números, respectivamente.
def get_statistics(results):
  total_graduados = 0
  media_graduados = 0
  periodo_max_graduados = results[0][0]
  periodo_min_graduados = results[0][0]
  max_graduados = results[0][1]
  min_graduados = results[0][1]

  for i in range(len(results)):
    if (results[i][1] < min_graduados):
      periodo_min_graduados = results[i][0]
      min_graduados = results[i][1]

    elif (results[i][1] > max_graduados):
      periodo_max_graduados = results[i][0]
      max_graduados = results[i][1]

    total_graduados += results[i][1]

  media_graduados = total_graduados / len(results)

  return [total_graduados, round(media_graduados, 2), periodo_min_graduados, 
    periodo_max_graduados, min_graduados, max_graduados]


# Função que monta a estrutura json para os alunos egressos (graduados), retorna um 
## array de objetos, onde cada objeto contém o semestre de vínculo e a quantidade de
### egressos daquele período.
def formatter_graduates(periods):
  response = []
  for i in range(len(periods)):
    response.append({"semestre_vinculo": periods[i][0], "qtd_egressos": periods[i][1]})

  return response


# Rota que retorna o número de alunos evadidos por período, a partir do id do motivo
## de cancelamento da matrícula.
def process_query_of_escaped(id):
  
  query = 'SELECT semestre_vinculo, count(*) AS qtd_evadidos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
    ' AND id_situacao_vinculo=' + str(id) + '\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'

  result = connection.select(query)
  
  retorno = []
  for i in range(len(result)):
    retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

  return retorno


# Rota que retorna um json com todos os números de evadidos por período de todos os 
## motivos, que podem ter do id 1 ao 9, inclusive.
@routes.route("/api/estatisticas/evadidos")
def escaped_from_period_from_all_types():
  motivos = []
  for i in range(1,10):
    motivos.append(process_query_of_escaped(i))

  return jsonify(motivos)


# Rota responsável por retornar o número de alunos evadidos do curso de Computação 
## agrupados por período, onde o id_motivo deve ser um valor entre 1 e 9, inclusive.
@routes.route("/api/estatisticas/evadidos/<int:id_motivo>")
def escaped_from_period(id_motivo):
  if (id_motivo >= 1 and id_motivo <= 9):

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
    return { "error": "Invalid resource" }, 404


# Rota responsável por retornar o número de alunos egressos (formados) do curso de 
## Computação e suas estatísticas de todos os períodos.
@routes.route("/api/estatisticas/egressos")
def graduates_by_period():

  # acesso aos route params (parâmetros que são passados no endereço da rota).
  args = request.args

  # Para rotas do tipo /api/estatisticas/egressos?periodo=2019.2, por exemplo.
  #retorna o número de egressos que o período informado na rota obteve.
  if (len(args) == 1):
    periodo = args.get('periodo')

    query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
      ' AND id_situacao_vinculo=' + str(constants.GRADUADO) + '\
      AND semestre_vinculo=\'' + str(periodo) + '\'\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = connection.select(query)

    # caso não hajam registros que correspondam a query passada
    if (len(result) == 0):
      return { "semestre_vinculo": periodo, "qtd_egressos": 0 }
    else:
      return jsonify(formatter_graduates(result))
  

  # Para rotas do tipo /api/estatisticas/egressos?minimo=1999.1&maximo=2010.2, por exemplo.
  ## retornam o número de egressos por período na faixa que foi especificada na rota, além
  ### de suas estatísticas
  elif (len(args) == 2):
    minimo = args.get('minimo')
    maximo = args.get('maximo')

    # Caso o periodo minimo do intervalo seja maior que o maximo ou então igual, retorna
    #uma mensagem de erro com código 404 not found.
    if (minimo > maximo or minimo == maximo):
      return { "error": "Parameters or invalid request" }, 404

    query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
      'AND id_situacao_vinculo=' + str(constants.GRADUADO) + \
      'AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\'\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = connection.select(query)
    statistics = get_statistics(result)

    return jsonify(total_graduados=statistics[0], media_graduados=statistics[1], 
      periodo_min_graduados=statistics[2], periodo_max_graduados=statistics[3],
      min_graduados=statistics[4], max_graduados=statistics[5], 
      periodos=formatter_graduates(result))

  # Para rotas do tipo /api/estatisticas/egressos, que retornam o número de egressos de
  ## todos os períodos até então cadastrados.
  else:

    query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
      ' AND id_situacao_vinculo=' + str(constants.GRADUADO) + '\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = connection.select(query)
    statistics = get_statistics(result)

    return jsonify(total_graduados=statistics[0], media_graduados=statistics[1], 
      periodo_min_graduados=statistics[2], periodo_max_graduados=statistics[3], 
      min_graduados=statistics[4], max_graduados=statistics[5], periodos=formatter_graduates(result))