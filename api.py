from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json
from flypy import *

app = Flask(__name__)
api = Api(app)
CORS(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Airports(Resource):
    def get(self):
        with open('flypy/data/airports.json') as json_data:
            d = json.load(json_data)
            trimmed = [{k: x[k] for k in ('name', 'iata_code', 'country')} for x in d]
            for x in trimmed:
                x["title"] = x.pop("name")
                x["price"] = x.pop("iata_code")
                x["description"] = x.pop("country")
            return trimmed


api.add_resource(HelloWorld, '/')
api.add_resource(Airports, '/airports')

if __name__ == '__main__':
    app.run(debug=True)
