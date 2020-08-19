from livereload import Server
from controllers import *
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

app.register_blueprint(routes)

### Swagger specific 
SWAGGER_URL = '/api/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
  SWAGGER_URL,
  API_URL,
  config={
    'app-name': "PDC Backend"
  }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end Swagger specific

if __name__ == '__main__':
  server = Server(app.wsgi_app)
  server.serve()