from flask import jsonify
from util import constants

# Função que organiza a resposta das queries da rota ativos e elabora um json com todos
## as chaves e valores correspondentes.
def response_json_to_active_route(dados):
  json_return = []

  for registro in dados:
    periodos_integralizados = int(registro[1])
    cred_obrig_int = int(registro[2])
    cred_opt_int = int(registro[3])
    cred_comp_int = int(registro[4])

    cred_comp_int = get_percent(cred_obrig_int, cred_opt_int, cred_comp_int)

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

# Calcula o percentual do curso concluído de cada aluno a partir dos créditos.
def get_percent(cred_obrig_int, cred_opt_int, cred_comp_int):
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
def response_json_to_csv_export(dados):
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

# Função auxiliar que retorna estatísticas sobre os egressos, informações como o total 
## de graduados em um determinado intervalo de tempo, média de graduados, períodos que
### tiveram mais e menos graduados e seus números, respectivamente.
def get_statistics(results):
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
def response_json_to_graduates_route(periods):
  response = []
  for i in range(len(periods)):
    response.append({
      "semestre_vinculo": periods[i][0], 
      "qtd_egressos": periods[i][1],
      "cra_medio": round(periods[i][2], 2),
    })

  return response

