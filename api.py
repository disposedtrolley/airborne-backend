from flask import Flask
from flask_restful import Resource, Api
import json
from flypy import *

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Airports(Resource):
    def get(self):
        with open('flypy/data/airports.json') as json_data:
            d = json.load(json_data)
            return [{k: x[k] for k in ('name', 'iata_code', 'country')} for x in d]


api.add_resource(HelloWorld, '/')
api.add_resource(Airports, '/airports')

if __name__ == '__main__':
    app.run(debug=True)
