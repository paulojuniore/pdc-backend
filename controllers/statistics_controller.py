# coding: utf-8
import sys
sys.path.append("../connection")
from Connection import Connection
from flask import Flask

app = Flask(__name__)

@app.route("/egressos")
def graduates_by_period():
  return {
    "message": "Teste de endpoint!"
  }
