# coding: utf-8
import sys
sys.path.append("./connection")
from Connection import Connection
from flask import jsonify
from util import constants

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


  # Calcula o percentual do curso concluído de cada aluno a partir dos créditos.
  def get_percent(self, cred_obrig_int, cred_opt_int, cred_comp_int):
    result = 0
    if (cred_comp_int == 0):
      pass
    elif (cred_comp_int == 4):
      result = 4
    elif (cred_comp_int == 8):
      result = 8
    else:
      result = max(0, min(8, cred_comp_int - 22))

    porcentagem = min(cred_obrig_int, 132) + min(cred_opt_int, 56) + result

    return (porcentagem / int(constants.TOTAL_CREDITOS)) * 100

  # Função que formata o json de resposta das rotas que geram os dados para exportar para
  ## o arquivo .csv. Essas rotas retornam informações sobre os alunos ativos, egressos ou
  ### evadidos.
  def response_json_to_csv_export(self, dados):
    json_return = []
   
    for registro in dados:
      ano_ingresso = registro[0][1:3]
      semestre_ingresso = registro[0][3]

      periodo_ingresso = ano_ingresso + "." + semestre_ingresso

      json_return.append({
        "matricula": registro[0],
        "periodo_ingresso": periodo_ingresso,
        "periodos_integralizados": registro[1],
        "cred_obrig_int": registro[2],
        "cred_opt_int": registro[3],
        "cred_comp_int": registro[4],
        "cota": registro[5],
        "genero": registro[6],
        "estado_civil": registro[7],
        "curriculo": registro[8],
        "cra": registro[9],
        "mc": registro[10],
        "iea": registro[11],
        "trancamentos_totais": registro[12],
        "matriculas_institucionais": registro[13],
        "mobilidade_estudantil": registro[14],
        "media_geral_ingresso": registro[15]
      })
    
    return jsonify(json_return)


  # Função que retorna informações sobre os alunos ativos do curso de Computação,
  ## informações estas que são a matrícula do aluno e a cred_comp_int concluída do 
  ### curso com base na quantidade de créditos que o aluno já possui.
  def get_actives(self):
    query = 'SELECT "DiscenteVinculo".matricula, "Discente".per_int, "Discente".cred_obrig_int, "Discente".cred_opt_int, "Discente".cred_comp_int \
      FROM "DiscenteVinculo"\
      INNER JOIN "Discente"\
        ON "DiscenteVinculo".cpf="Discente".cpf\
      WHERE "DiscenteVinculo".id_curso=' + self.id_computacao + '\
      AND "Discente".id_situacao=' + self.id_ativo + '\
      AND "DiscenteVinculo".id_situacao_vinculo=' + self.id_regular + '\
      AND "Discente".per_int > 0'

    result = self.connection.select(query)

    json_return = []
    for registro in result:
      periodos_integralizados = int(registro[1])
      cred_obrig_int = int(registro[2])
      cred_opt_int = int(registro[3])
      cred_comp_int = int(registro[4])

      cred_comp_int = self.get_percent(cred_obrig_int, cred_opt_int, cred_comp_int)

      ano_ingresso = registro[0][1:3]
      semestre_ingresso = registro[0][3]

      periodo_ingresso = ano_ingresso + "." + semestre_ingresso
      
      json_return.append({ 
        "matricula": registro[0], 
        "periodo_ingresso": periodo_ingresso,
        "periodos_integralizados": periodos_integralizados, 
        "porcentagem_concluida": round(cred_comp_int, 2)
      })

    return jsonify(json_return)

  
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

    return self.response_json_to_csv_export(result)


  # Função auxiliar que retorna estatísticas sobre os egressos, informações como o total 
  ## de graduados em um determinado intervalo de tempo, média de graduados, períodos que
  ### tiveram mais e menos graduados e seus números, respectivamente.
  def get_statistics(self, results):
    total_graduados = 0
    media_graduados = 0
    periodo_max_graduados = results[0][0]
    periodo_min_graduados = results[0][0]
    max_graduados = results[0][1]
    min_graduados = results[0][1]
    soma_cras = 0

    for i in range(len(results)):
      if (results[i][1] < min_graduados):
        periodo_min_graduados = results[i][0]
        min_graduados = results[i][1]

      elif (results[i][1] > max_graduados):
        periodo_max_graduados = results[i][0]
        max_graduados = results[i][1]

      total_graduados += results[i][1]
      soma_cras += results[i][2]

    media_graduados = total_graduados / len(results)
    media_cras = soma_cras / len(results)

    return [total_graduados, round(media_graduados, 2), periodo_min_graduados, 
      periodo_max_graduados, min_graduados, max_graduados, round(media_cras, 2)]


  # Função auxiliar que monta a estrutura json para os alunos egressos (graduados), 
  ## retorna um array de objetos, onde cada objeto contém o semestre de vínculo e a
  ### quantidade de egressos daquele período.
  def formatter_graduates(self, periods):
    response = []
    for i in range(len(periods)):
      response.append({
        "semestre_vinculo": periods[i][0], 
        "qtd_egressos": periods[i][1],
        "cra_medio": round(periods[i][2], 2),
      })

    return response


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
        return jsonify(self.formatter_graduates(result))
    

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
      statistics = self.get_statistics(result)

      return jsonify(
        total_graduados=statistics[0], 
        media_graduados=statistics[1], 
        periodo_min_graduados=statistics[2], 
        periodo_max_graduados=statistics[3],
        min_graduados=statistics[4], 
        max_graduados=statistics[5],
        cra_medio=statistics[6], 
        periodos=self.formatter_graduates(result)
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
      statistics = self.get_statistics(result)

      return jsonify(
        total_graduados=statistics[0], 
        media_graduados=statistics[1], 
        periodo_min_graduados=statistics[2], 
        periodo_max_graduados=statistics[3], 
        min_graduados=statistics[4], 
        max_graduados=statistics[5], 
        cra_medio=statistics[6],
        periodos=self.formatter_graduates(result)
      )
  

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

      return self.response_json_to_csv_export(result)

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

      return self.response_json_to_csv_export(result)

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

      return self.response_json_to_csv_export(result)


  # Função que retorna o número de alunos evadidos por período (a partir do id do motivo
  ## de cancelamento da matrícula) de um único período passado.
  def process_query_of_one_period(self, id, periodo):

    query = 'SELECT semestre_vinculo, count(*) AS qtd_evadidos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + self.id_computacao + \
      ' AND id_situacao_vinculo=' + str(id) + '\
      AND semestre_vinculo=\'' + str(periodo) + '\'\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = self.connection.select(query)
    
    retorno = []
    for i in range(len(result)):
      retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

    return retorno


  # Função que retorna o número de alunos evadidos por período (a partir do id do motivo
  ## de cancelamento da matrícula) de um intervalo de períodos passados.
  def process_query_of_interval_of_the_periods(self, id, minimo, maximo):

    query = 'SELECT semestre_vinculo, count(*) AS qtd_egressos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + self.id_computacao + \
      'AND id_situacao_vinculo=' + str(id) + \
      'AND semestre_vinculo BETWEEN \'' + str(minimo) + '\' AND \'' + str(maximo) + '\'\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = self.connection.select(query)
    
    retorno = []
    for i in range(len(result)):
      retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

    return retorno


  # Função que retorna o número de alunos evadidos por período, a partir do id do motivo
  ## de cancelamento da matrícula, de todos os períodos registrados.
  def process_query_of_escaped(self, id):

    query = 'SELECT semestre_vinculo, count(*) AS qtd_evadidos\
      FROM "DiscenteVinculo"\
      WHERE id_curso=' + self.id_computacao + \
      ' AND id_situacao_vinculo=' + str(id) + '\
      GROUP BY semestre_vinculo\
      ORDER BY semestre_vinculo'

    result = self.connection.select(query)
    
    retorno = []
    for i in range(len(result)):
      retorno.append({"semestre": result[i][0], "tag"+str(id): result[i][1]})

    return retorno


  # Fazendo a junção entre os 9 arrays de evadidos pelos motivos de 1 a 9, para que o
  ## array tenha o formato { "periodo": { "tag1": 0, "tag2": 0, ..., "tag9": 0 }, ... },
  ### onde tag(i) significa o número de evadidos pelo motivo (i) naquele período, sendo
  #### "i" um valor entre 1 e 9.
  def join_results_of_escaped_query(self, results):
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
  def fill_tag_list_with_zeros(self, json):
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
  def prepare_json_to_return(self, json):
    json_response = []
    for i in json:
      json_response.append({ "periodo": i, "tags": json[i] })
    
    return json_response


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
        evadidos_por_motivo.append(self.process_query_of_one_period(i, periodo))

      joined_results = self.join_results_of_escaped_query(evadidos_por_motivo)

      # Caso não hajam resultados para o periodo especificado, é retornado um json com
      ## todas as tags zeradas.
      if (len(joined_results) == 0):
        retorno =  {"periodo": periodo, "tags": { "tag1": 0, "tag2": 0, "tag3": 0, 
          "tag4": 0, "tag5": 0, "tag6": 0, "tag7": 0, "tag8": 0, "tag9": 0 } }
        
        return jsonify(retorno)

      joined_results_with_zeros = self.fill_tag_list_with_zeros(joined_results)

      json_return = self.prepare_json_to_return(joined_results_with_zeros)

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
        evadidos_por_motivo.append(self.process_query_of_interval_of_the_periods(i, minimo, maximo))

      joined_results = self.join_results_of_escaped_query(evadidos_por_motivo)
      
      joined_results_with_zeros = self.fill_tag_list_with_zeros(joined_results)

      json_return = self.prepare_json_to_return(joined_results_with_zeros)

      return jsonify(json_return)
      
    # Caso não seja passado parâmetro algum na rota, são trazidos os dados de todos os períodos
    ## já cadastrados
    else:
      
      evadidos_por_motivo = []
      for i in range(1, 10):
        evadidos_por_motivo.append(self.process_query_of_escaped(i))

      joined_results = self.join_results_of_escaped_query(evadidos_por_motivo)

      joined_results_with_zeros = self.fill_tag_list_with_zeros(joined_results)

      json_return = self.prepare_json_to_return(joined_results_with_zeros)
      
      return jsonify(json_return)  

