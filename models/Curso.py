# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from util import constants

sys.path.append("./models/util")
from StatisticsExternalFunctions import (response_json_to_active_route, get_percent,
  response_json_to_csv_export, get_statistics, response_json_to_graduates_route,
  process_query_of_one_period, join_results_of_escaped_query, fill_tag_list_with_zeros,
  response_json_to_escaped_route, process_query_of_escaped, process_query_of_interval_of_the_periods)

class Curso():

  # Construtor da classe
  def __init__(self):
    # Instância da conexão ao banco de dados.
    self.connection = Connection()

    # Queries para setar os id's das constantes que são usadas nas consultas realizadas
    ## na Classe.
    query_id_curso = 'SELECT "Curso".id FROM "Curso" \
      WHERE "Curso".nome=\'' + str(constants.COMPUTACAO_VALUE) + '\''

    query_id_regular = 'SELECT "SituacaoVinculo".id FROM "SituacaoVinculo" \
      WHERE "SituacaoVinculo".descricao=\'' + str(constants.REGULAR_VALUE) + '\''

    query_id_aprovado = 'SELECT "SituacaoDisciplina".id FROM "SituacaoDisciplina" \
      WHERE "SituacaoDisciplina".descricao=\'' + constants.APROVADO_VALUE + '\''

    query_id_graduado = 'SELECT "SituacaoVinculo".id FROM "SituacaoVinculo" \
      WHERE "SituacaoVinculo".descricao=\'' + str(constants.GRADUADO_VALUE) + '\''

    query_id_ativo = 'SELECT "SituacaoDiscente".id FROM "SituacaoDiscente" \
      WHERE "SituacaoDiscente".descricao=\'' + str(constants.ATIVO_VALUE) + '\''

    # id's das constantes
    self.id_computacao = str(self.connection.select(query_id_curso)[0][0])
    self.id_regular = str(self.connection.select(query_id_regular)[0][0])
    self.id_aprovado = str(self.connection.select(query_id_aprovado)[0][0])
    self.id_graduado = str(self.connection.select(query_id_graduado)[0][0])
    self.id_ativo = str(self.connection.select(query_id_ativo)[0][0])


  # Função que retorna informações sobre os alunos ativos do curso de Computação,
  ## informações estas que são a matrícula do aluno e a cred_comp_int concluída do 
  ### curso com base na quantidade de créditos que o aluno já possui.
  def get_actives(self, args):
    if (len(args) == 1):
      periodo = args.get('de')

      query = 'SELECT "DiscenteVinculo".matricula, "Discente".per_int, "Discente".cred_obrig_int, "Discente".cred_opt_int, "Discente".cred_comp_int \
        FROM "DiscenteVinculo" \
        INNER JOIN "Discente" \
          ON "DiscenteVinculo".cpf = "Discente".cpf \
        WHERE "DiscenteVinculo".id_curso = ' + self.id_computacao + ' \
        AND "Discente".id_situacao = ' + self.id_ativo + ' \
        AND "Discente".per_int > 0 \
        AND "DiscenteVinculo".semestre_vinculo=\'' + str(periodo) + '\''

      result = self.connection.select(query)

      return response_json_to_active_route(result)

    elif (len(args) == 2):
      minimo = args.get('de')
      maximo = args.get('ate')

      # Caso o periodo minimo do intervalo seja maior que o maximo ou então igual, retorna
      ## uma mensagem de erro com código 404 not found.
      if (minimo > maximo or minimo == maximo):
        return { "error": "Parameters or invalid request" }, 404

      query = 'SELECT "DiscenteVinculo".matricula, "Discente".per_int, "Discente".cred_obrig_int, "Discente".cred_opt_int, "Discente".cred_comp_int \
        FROM "DiscenteVinculo"\
        INNER JOIN "Discente"\
          ON "DiscenteVinculo".cpf="Discente".cpf\
        WHERE "DiscenteVinculo".id_curso=' + self.id_computacao + '\
        AND "Discente".id_situacao=' + self.id_ativo + '\
        AND "Discente".per_int > 0 \
        AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\''

      result = self.connection.select(query)

      return response_json_to_active_route(result)

    else:

      query = 'SELECT "DiscenteVinculo".matricula, "Discente".per_int, "Discente".cred_obrig_int, "Discente".cred_opt_int, "Discente".cred_comp_int \
        FROM "DiscenteVinculo"\
        INNER JOIN "Discente"\
          ON "DiscenteVinculo".cpf="Discente".cpf\
        WHERE "DiscenteVinculo".id_curso=' + self.id_computacao + '\
        AND "Discente".id_situacao=' + self.id_ativo + '\
        AND "DiscenteVinculo".id_situacao_vinculo=' + self.id_regular + '\
        AND "Discente".per_int > 0'

      result = self.connection.select(query)

      return response_json_to_active_route(result)

  
  # Função que retorna os dados para geração do arquivo csv de alunos ativos.
  def export_to_csv_actives(self):
    query = 'SELECT "DiscenteVinculo".matricula, per_int, cred_obrig_int, cred_opt_int, \
        cred_comp_int, "Cota".descricao, "Genero".descricao, "EstadoCivil".descricao, \
        "Discente".curriculo, cra, mc, iea, tranc, mat_inst, mob_estudantil, \
        media_geral_ingresso \
      FROM "DiscenteVinculo" \
      INNER JOIN "Discente" \
        ON "DiscenteVinculo".cpf = "Discente".cpf \
      INNER JOIN "Cota" \
        ON "Discente".id_cota = "Cota".id \
      INNER JOIN "Genero" \
        ON "Discente".id_genero = "Genero".id \
      INNER JOIN "EstadoCivil" \
        ON "Discente".id_estado_civil = "EstadoCivil".id \
      WHERE "DiscenteVinculo".id_curso = ' + self.id_computacao + '\
      AND "Discente".id_situacao = ' + self.id_ativo + '\
      AND "DiscenteVinculo".id_situacao_vinculo = ' + self.id_regular + '\
      AND "Discente".per_int > 0' 

    result = self.connection.select(query)

    return response_json_to_csv_export(result)


  # Função responsável por retornar o número de alunos egressos (formados) do curso de 
  ## Computação e suas estatísticas de todos os períodos.
  def get_graduates(self, args):

    # Para rotas do tipo /api/estatisticas/egressos?de=2019.2, por exemplo.
    ## Retorna o número de egressos que o período informado na rota obteve.
    if (len(args) == 1):
      periodo = args.get('de')

      query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos, avg(cra) AS cra_medio \
        FROM "DiscenteVinculo" \
        INNER JOIN "Discente" \
          ON "DiscenteVinculo".cpf = "Discente".cpf \
        WHERE id_curso=' + self.id_computacao + \
        ' AND id_situacao_vinculo=' + self.id_graduado + ' \
        AND semestre_vinculo=\'' + str(periodo) + '\' \
        GROUP BY semestre_vinculo \
        ORDER BY semestre_vinculo'

      result = self.connection.select(query)

      # Caso não hajam registros que correspondam a query passada.
      if (len(result) == 0):
        return { 
          "semestre_vinculo": periodo, 
          "qtd_egressos": 0,
          "cra_medio": 0 
        }
      else:
        return jsonify(response_json_to_graduates_route(result))
    

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

      query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos, avg(cra) AS cra_medio \
        FROM "DiscenteVinculo" \
        INNER JOIN "Discente" \
          ON "DiscenteVinculo".cpf = "Discente".cpf \
        WHERE id_curso=' + self.id_computacao + \
        'AND id_situacao_vinculo=' + self.id_graduado + \
        'AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\'\
        GROUP BY semestre_vinculo\
        ORDER BY semestre_vinculo'

      result = self.connection.select(query)
      statistics = get_statistics(result)

      return jsonify(
        total_graduados=statistics[0], 
        media_graduados=statistics[1], 
        periodo_min_graduados=statistics[2], 
        periodo_max_graduados=statistics[3],
        min_graduados=statistics[4], 
        max_graduados=statistics[5],
        cra_medio=statistics[6], 
        periodos=response_json_to_graduates_route(result)
      )

    # Para rotas do tipo '.../api/estatisticas/egressos', que retornam o número de egressos de
    ## todos os períodos até então cadastrados.
    else:
      query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos, avg(cra) AS cra_medio \
        FROM "DiscenteVinculo" \
        INNER JOIN "Discente" \
          ON "DiscenteVinculo".cpf = "Discente".cpf \
        WHERE id_curso=' + self.id_computacao + \
        ' AND id_situacao_vinculo=' + self.id_graduado + '\
        GROUP BY semestre_vinculo\
        ORDER BY semestre_vinculo'

      result = self.connection.select(query)
      statistics = get_statistics(result)

      return jsonify(
        total_graduados=statistics[0], 
        media_graduados=statistics[1], 
        periodo_min_graduados=statistics[2], 
        periodo_max_graduados=statistics[3], 
        min_graduados=statistics[4], 
        max_graduados=statistics[5], 
        cra_medio=statistics[6],
        periodos=response_json_to_graduates_route(result)
      )
  

  # Função responsável por buscar os dados dos alunos egressos e retorná-los para que o
  ## arquivo .csv possa ser gerado.
  def export_to_csv_graduates(self, args):

    if (len(args) == 1):
      periodo = args.get('de')

      query = 'SELECT matricula, per_int, cred_obrig_int, cred_opt_int, cred_comp_int, \
        "Cota".descricao, "Genero".descricao, "EstadoCivil".descricao, curriculo, cra, \
        mc, iea, tranc, mat_inst, mob_estudantil, media_geral_ingresso \
      FROM "Discente" \
      INNER JOIN "DiscenteVinculo" \
        ON "Discente".cpf = "DiscenteVinculo".cpf \
      INNER JOIN "Cota" \
        ON "Discente".id_cota = "Cota".id \
      INNER JOIN "Genero" \
        ON "Discente".id_genero = "Genero".id \
      INNER JOIN "EstadoCivil" \
        ON "Discente".id_estado_civil = "EstadoCivil".id \
      WHERE id_curso = ' + self.id_computacao + ' \
      AND id_situacao_vinculo = ' + self.id_graduado + ' \
      AND semestre_vinculo=\'' + str(periodo) + '\' \
      ORDER BY semestre_ingresso'

      result = self.connection.select(query)

      return response_json_to_csv_export(result)

    elif (len(args) == 2):
      minimo = args.get('de')
      maximo = args.get('ate')

      # Caso o periodo minimo do intervalo seja maior que o maximo ou então igual, retorna
      ## uma mensagem de erro com código 404 not found.
      if (minimo > maximo or minimo == maximo):
        return { "error": "Parameters or invalid request" }, 404

      query = 'SELECT matricula, per_int, cred_obrig_int, cred_opt_int, cred_comp_int, \
          "Cota".descricao, "Genero".descricao, "EstadoCivil".descricao, curriculo, cra, \
          mc, iea, tranc, mat_inst, mob_estudantil, media_geral_ingresso \
        FROM "Discente" \
        INNER JOIN "DiscenteVinculo" \
          ON "Discente".cpf = "DiscenteVinculo".cpf \
        INNER JOIN "Cota" \
          ON "Discente".id_cota = "Cota".id \
        INNER JOIN "Genero" \
          ON "Discente".id_genero = "Genero".id \
        INNER JOIN "EstadoCivil" \
          ON "Discente".id_estado_civil = "EstadoCivil".id \
        WHERE id_curso = ' + self.id_computacao + ' \
        AND id_situacao_vinculo = ' + self.id_graduado + ' \
        AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\'\
        ORDER BY semestre_ingresso'

      result = self.connection.select(query)

      return response_json_to_csv_export(result)

    else:
      query = 'SELECT matricula, per_int, cred_obrig_int, cred_opt_int, cred_comp_int, \
          "Cota".descricao, "Genero".descricao, "EstadoCivil".descricao, curriculo, cra, \
          mc, iea, tranc, mat_inst, mob_estudantil, media_geral_ingresso \
        FROM "Discente" \
        INNER JOIN "DiscenteVinculo" \
          ON "Discente".cpf = "DiscenteVinculo".cpf \
        INNER JOIN "Cota" \
          ON "Discente".id_cota = "Cota".id \
        INNER JOIN "Genero" \
          ON "Discente".id_genero = "Genero".id \
        INNER JOIN "EstadoCivil" \
          ON "Discente".id_estado_civil = "EstadoCivil".id \
        WHERE id_curso = ' + self.id_computacao + '\
        AND id_situacao_vinculo = ' + self.id_graduado + '\
        ORDER BY semestre_ingresso'

      result = self.connection.select(query)

      return response_json_to_csv_export(result)


  # Função que retorna um json com todos os números de evadidos por período de todos os 
  ## motivos, que podem ter do id 1 ao 9, inclusive.
  def get_escaped(self, args):
    # Verifica se foi passado somente um parâmetro na rota, que no caso, é o período
    ## a ser consultado o número de evadidos.
    if (len(args) == 1):
      periodo = args.get('de')

      # Processando queries com os ID's de 1 a 9 e armazenando todos os resultados em uma lista,
      ## para posteriormente fazer um merge dos resultados.
      evadidos_por_motivo = []
      for i in range(1, 10):
        evadidos_por_motivo.append(process_query_of_one_period(self.id_computacao, i, periodo))

      joined_results = join_results_of_escaped_query(evadidos_por_motivo)

      # Caso não hajam resultados para o periodo especificado, é retornado um json com
      ## todas as tags zeradas.
      if (len(joined_results) == 0):
        retorno =  {"periodo": periodo, "tags": { "tag1": 0, "tag2": 0, "tag3": 0, 
          "tag4": 0, "tag5": 0, "tag6": 0, "tag7": 0, "tag8": 0, "tag9": 0 } }
        
        return jsonify(retorno)

      joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

      json_return = response_json_to_escaped_route(joined_results_with_zeros)

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
        evadidos_por_motivo.append(process_query_of_interval_of_the_periods(self.id_computacao, i, minimo, maximo))

      joined_results = join_results_of_escaped_query(evadidos_por_motivo)
      
      joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

      json_return = response_json_to_escaped_route(joined_results_with_zeros)

      return jsonify(json_return)
      
    # Caso não seja passado parâmetro algum na rota, são trazidos os dados de todos os períodos
    ## já cadastrados
    else:
      
      evadidos_por_motivo = []
      for i in range(1, 10):
        evadidos_por_motivo.append(process_query_of_escaped(self.id_computacao, i))

      joined_results = join_results_of_escaped_query(evadidos_por_motivo)

      joined_results_with_zeros = fill_tag_list_with_zeros(joined_results)

      json_return = response_json_to_escaped_route(joined_results_with_zeros)
      
      return jsonify(json_return)  

