from api.v1.endpoints import v1_blueprint
from flask import Flask
from waitress import serve

app = Flask(__name__)
app.register_blueprint(v1_blueprint, url_prefix = '/api/v1')
print("Server Started")
if __name__ == "__main__":
    app.run(host= "0.0.0.0", port = 8000)
