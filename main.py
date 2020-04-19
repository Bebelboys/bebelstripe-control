import LEDWall
import FFT
import SharedVariables
import threading
import sys
import time
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

shared_vars = SharedVariables.SharedVariables()

flask_app = Flask(__name__)
flask_api = Api(flask_app)

parser = reqparse.RequestParser()
parser.add_argument('primaryColor', type=int, action='append')
parser.add_argument('secondaryColor', type=int, action='append')


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class Color(Resource):
    def options(self):
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        args = parser.parse_args()
        print(args)
        if args['primaryColor']:
            shared_vars.primaryColor = args['primaryColor']
        if args['secondaryColor']:
            shared_vars.secondaryColor = args['secondaryColor']
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}


flask_api.add_resource(HelloWorld, '/')
flask_api.add_resource(Color, '/color')


def main():
    try:
        ledwall = LEDWall.LEDWall()
        fft = FFT.FFT()

        t1 = threading.Thread(target=ledwall.music_spectrum, args=(shared_vars,))
        t1.daemon = True
        t1.start()
        t2 = threading.Thread(target=fft.start, args=(shared_vars,))
        t2.daemon = True
        t2.start()
        t3 = threading.Thread(target=flask_app.run, args=('192.168.120.13', 80,))
        t3.daemon = True
        t3.start()

        while True:
            time.sleep(5)

    except KeyboardInterrupt:
        print("Terminated by user ...")
        sys.exit(0)

    except Exception as e:
        print("EXCEPTION CATCHED")
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
