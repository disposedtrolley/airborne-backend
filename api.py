from flask import Flask
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json
from flypy import *

app = Flask(__name__)
api = Api(app)
CORS(app)


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


class Flights(Resource):
    args = {
        'origin': fields.Str(
            required=True
        ),
        'dest': fields.Str(
            required=True
        ),
        'adults': fields.Str(
            required=True
        ),
        'children': fields.Str(
            required=False
        ),
        'dept_date': fields.Str(
            required=True
        ),
        'return_date': fields.Str(
            required=False
        )
    }
    @use_kwargs(args)
    def get(self, origin, dest, adults, children, dept_date, return_date):
        query = Query()
        query.add_origin(origin)
        query.add_dest(dest)
        if children:
            query.add_pax(int(adults), int(children))
        else:
            query.add_pax(int(adults))
        query.add_dept_date(dept_date)
        if return_date:
            query.add_return_date(return_date)
        response = query.send()
        trips = response.get_trips()

        output = {
          "options": []
        }

        for trip_option in trips:

            trip_data = {
                "cost": trip_option.get_cost(),
                "onward_flight": {
                    "legs": [],
                    "layovers": []
                },
                "return_flight": {
                    "legs": [],
                    "layovers": []
                }
            }

            journeys = trip_option.get_journeys()
            for i in range(len(journeys)):
                curr_journey = journeys[i]
                legs = curr_journey.get_legs()
                layovers = curr_journey.get_layovers()
                if i == 0:
                    # onward flight
                    for leg in legs:
                        origin = leg.get_origin()
                        dest = leg.get_dest()
                        flight = leg.get_flight()
                        aircraft = leg.get_aircraft()
                        trip_data["onward_flight"]["legs"].append(
                            {
                                "origin_name": origin["name"],
                                "origin_city": origin["city"],
                                "origin_code": origin["code"],
                                "dest_name": dest["name"],
                                "dest_city": dest["city"],
                                "dest_code": dest["code"],
                                "duration": leg.get_duration(),
                                "dept_time": str(leg.get_dept_time()),
                                "arr_time": str(leg.get_arr_time()),
                                "flight": flight["name"] + " " + flight["carrier"] + flight["number"],
                                "aircraft": aircraft["name"] + " (" + aircraft["code"] + ")"
                            }
                        )
                    for layover in layovers:
                        airport = layover.get_layover_airport()
                        trip_data["onward_flight"]["layovers"].append(
                            {
                                "airport_name": airport["name"],
                                "airport_code": airport["code"],
                                "duration": layover.get_layover_dur()
                            }
                        )
                else:
                    # return flight
                    for leg in legs:
                        origin = leg.get_origin()
                        dest = leg.get_dest()
                        flight = leg.get_flight()
                        aircraft = leg.get_aircraft()
                        trip_data["return_flight"]["legs"].append(
                            {
                                "origin_name": origin["name"],
                                "origin_city": origin["city"],
                                "origin_code": origin["code"],
                                "dest_name": dest["name"],
                                "dest_city": dest["city"],
                                "dest_code": dest["code"],
                                "duration": leg.get_duration(),
                                "dept_time": str(leg.get_dept_time()),
                                "arr_time": str(leg.get_arr_time()),
                                "flight": flight["name"] + " " + flight["carrier"] + flight["number"],
                                "aircraft": aircraft["name"] + " (" + aircraft["code"] + ")"
                            }
                        )
                    for layover in layovers:
                        airport = layover.get_layover_airport()
                        trip_data["return_flight"]["layovers"].append(
                            {
                                "airport_name": airport["name"],
                                "airport_code": airport["code"],
                                "duration": layover.get_layover_dur()
                            }
                        )
            output["options"].append(trip_data)
        return output


api.add_resource(Airports, '/airports')
api.add_resource(Flights, '/flights')

if __name__ == '__main__':
    app.run(debug=True)
