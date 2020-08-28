# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify, request
from . import routes
from util import constants

# Instância da conexão ao banco de dados.
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


# Função que retorna o número de alunos evadidos por período (a partir do id do motivo
## de cancelamento da matrícula) de um único período passado.
def process_query_of_one_period(id, periodo):

  query = 'SELECT semestre_vinculo, count(*) AS qtd_evadidos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
    ' AND id_situacao_vinculo=' + str(id) + '\
    AND semestre_vinculo=\'' + str(periodo) + '\'\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'

  result = connection.select(query)
  
  retorno = []
  for i in range(len(result)):
    retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

  return retorno


# Função que retorna o número de alunos evadidos por período (a partir do id do motivo
## de cancelamento da matrícula) de um intervalo de períodos passados.
def process_query_of_interval_of_the_periods(id, minimo, maximo):

  query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
    FROM "DiscenteVinculo"\
    WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
    'AND id_situacao_vinculo=' + str(id) + \
    'AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\'\
    GROUP BY semestre_vinculo\
    ORDER BY semestre_vinculo'

  result = connection.select(query)
  
  retorno = []
  for i in range(len(result)):
    retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

  return retorno


# Função que retorna o número de alunos evadidos por período, a partir do id do motivo
## de cancelamento da matrícula, de todos os períodos registrados.
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


# Fazendo a junção entre os 9 arrays de evadidos pelos motivos de 1 a 9, para que o
## array tenha o formato { "periodo": { "tag1": 0, "tag2": 0, ..., "tag9": 0 }, ... },
### onde tag(i) significa o número de evadidos pelo motivo (i) naquele período, sendo
#### "i" um valor entre 1 e 9.
def join_results_of_escaped_query(results):
  dic_periodos = {}
  for i in range(len(results)):
    for j in range(len(results[i])):
      if (results[i][j]['semestre'] in dic_periodos):
        dic_periodos[str(results[i][j]['semestre'])]['tag'+str(i+1)] = results[i][j]['tag'+str(i+1)]
      else:
        dic_periodos[str(results[i][j]['semestre'])] = { 'tag'+str(i+1): results[i][j]['tag'+str(i+1)] }

  return dic_periodos


# Preenchendo com 0 as tags que não existem no objeto de cada período. Exemplo: caso o
## período X só tenha evadidos em "tag1", "tag2" e "tag3", o trecho abaixo irá preencher
### o objeto com o restante das tags até a 9, todas com o valor 0.    
def fill_tag_list_with_zeros(json):
  for i in json:
    for j in range(1,10):
      if ('tag'+str(j) in json[i]):
        pass
      else:
        json[i]['tag'+str(j)] = 0
  
  return json


# Função que prepara o json para retorno, onde cada objeto irá possui a chave semestre com
## o período e outra chave tags, que correspondem as 9 tags que representam a quantidade
### de evadidos pelo motivo i, onde i é um número entre 1 e 9, inclusive.
def prepare_json_to_return(json):
  json_response = []
  for i in json:
    json_response.append({ "periodo": i, "tags": json[i] })
  
  return json_response


# Rota que retorna um json com todos os números de evadidos por período de todos os 
## motivos, que podem ter do id 1 ao 9, inclusive.
@routes.route("/api/estatisticas/evadidos")
def escaped_from_period():

  # Acesso aos route params (parâmetros que são passados no endereço da rota).
  args = request.args

  # Verifica se foi passado somente um parâmetro na rota, que no caso, é o período
  ## a ser consultado o número de evadidos.
  if (len(args) == 1):
    periodo = args.get('de')

    # Processando queries com os ID's de 1 a 9 e armazenando todos os resultados em uma lista,
    ## para posteriormente fazer um merge dos resultados.
    evadidos_por_motivo = []
    for i in range(1, 10):
      evadidos_por_motivo.append(process_query_of_one_period(i, periodo))

    joined_results = join_results_of_escaped_query(evadidos_por_motivo)

    # Caso não hajam resultados para o periodo especificado, é retornado um json com
    ## todas as tags zeradas.
    if (len(joined_results) == 0):
      retorno =  {"periodo": periodo, "tags": { "tag1": 0, "tag2": 0, "tag3": 0, 
        "tag4": 0, "tag5": 0, "tag6": 0, "tag7": 0, "tag8": 0, "tag9": 0 } }
      
      return jsonify(retorno)

    joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

    json_return = prepare_json_to_return(joined_results_with_zeros)

    return jsonify(json_return)

  # Verifica se foram passados dois parâmetro na rota, que no caso, é o período de início
  ## e fim para a consulta nesse intervalo sobre o número de evadidos por período por todos
  ### os tipos de evasão.
  elif (len(args) == 2):
    minimo = args.get('de')
    maximo = args.get('ate')

    # Caso o periodo minimo do intervalo seja maior que o maximo ou então igual, retorna
    ## uma mensagem de erro com código 404 not found.
    if (minimo > maximo or minimo == maximo):
      return { "error": "Parameters or invalid request" }, 404

    evadidos_por_motivo = []
    for i in range(1, 10):
      evadidos_por_motivo.append(process_query_of_interval_of_the_periods(i, minimo, maximo))

    joined_results = join_results_of_escaped_query(evadidos_por_motivo)
    
    joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

    json_return = prepare_json_to_return(joined_results_with_zeros)

    return jsonify(json_return)
    
  # Caso não seja passado parâmetro algum na rota, são trazidos os dados de todos os períodos
  ## já cadastrados
  else:
    
    evadidos_por_motivo = []
    for i in range(1, 10):
      evadidos_por_motivo.append(process_query_of_escaped(i))

    joined_results = join_results_of_escaped_query(evadidos_por_motivo)

    joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

    json_return = prepare_json_to_return(joined_results_with_zeros)
    
    return jsonify(json_return)  


# Rota responsável por retornar o número de alunos egressos (formados) do curso de 
## Computação e suas estatísticas de todos os períodos.
@routes.route("/api/estatisticas/egressos")
def graduates_by_period():

  # Acesso aos route params (parâmetros que são passados no endereço da rota).
  args = request.args

  # Para rotas do tipo /api/estatisticas/egressos?de=2019.2, por exemplo.
  ## Retorna o número de egressos que o período informado na rota obteve.
  if (len(args) == 1):
    periodo = args.get('de')

    query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + str(constants.COMPUTACAO_KEY) + \
      ' AND id_situacao_vinculo=' + str(constants.GRADUADO) + '\
      AND semestre_vinculo=\'' + str(periodo) + '\'\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = connection.select(query)

    # Caso não hajam registros que correspondam a query passada.
    if (len(result) == 0):
      return { "semestre_vinculo": periodo, "qtd_egressos": 0 }
    else:
      return jsonify(formatter_graduates(result))
  

  # Para rotas do tipo '.../api/estatisticas/egressos?de=1999.1&ate=2010.2', por exemplo.
  ## retornam o número de egressos por período na faixa que foi especificada na rota, além
  ### de suas estatísticas.
  elif (len(args) == 2):
    minimo = args.get('de')
    maximo = args.get('ate')

    # Caso o periodo minimo do intervalo seja maior que o maximo ou então igual, retorna
    ## uma mensagem de erro com código 404 not found.
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

  # Para rotas do tipo '.../api/estatisticas/egressos', que retornam o número de egressos de
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