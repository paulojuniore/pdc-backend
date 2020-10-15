from livereload import Server
from controllers import *
from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from properties import HOST, PORT

app = Flask(__name__)

cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(routes)

### Swagger specific 
SWAGGER_URL = '/api/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
  SWAGGER_URL,
  API_URL,
  config={
    'app-name': "Eureca - API REST"
  }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end Swagger specific

if __name__ == '__main__':
  server = Server(app.wsgi_app)
  server.serve(host=HOST, port=PORT)