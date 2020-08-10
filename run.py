from livereload import Server
from controllers import *
from flask import Flask

app = Flask(__name__)

app.register_blueprint(routes)

if __name__ == '__main__':
  server = Server(app.wsgi_app)
  server.serve()