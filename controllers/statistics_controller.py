# coding: utf-8
import sys
from flask import request
from flask_cors import cross_origin
from . import routes
sys.path.append("./models")
from Curso import Curso

# Instância do model Curso que gerencia informações gerais sobre alunos do curso.
curso = Curso()

# Rota que retorna um json com todos os números de evadidos por período de todos os 
## motivos, que podem ter do id 1 ao 9, inclusive.
@routes.route("/api/estatisticas/evadidos")
@cross_origin()
def escaped_from_period():

  # Acesso aos route params (parâmetros que são passados no endereço da rota).
  args = request.args

  return curso.get_escaped(args) 

# Rota responsável por retornar o número de alunos egressos (formados) do curso de 
## Computação e suas estatísticas de todos os períodos.
@routes.route("/api/estatisticas/egressos")
@cross_origin()
def graduates_by_period():

  # Acesso aos route params (parâmetros que são passados no endereço da rota).
  args = request.args

  return curso.get_graduates(args)

# Rota responsável por retornar informações sobre os alunos ativos do curso de Computação,
## informações estas que são a matrícula do aluno e a porcentagem concluída do curso com 
### base na quantidade de créditos que o aluno já possui.
@routes.route("/api/estatisticas/ativos")
@cross_origin()
def active_students():
  return curso.get_actives()

# Rota responsável por retornar as informações que vão compor o arquivo .csv de alunos
## ativos.
@routes.route("/api/estatisticas/ativos/csv")
@cross_origin()
def export_to_csv_actives():
  return curso.export_to_csv_actives()

@routes.route("/api/estatisticas/egressos/csv")
@cross_origin()
def export_to_csv_graduates():
  args = request.args

  return curso.export_to_csv_graduates(args)