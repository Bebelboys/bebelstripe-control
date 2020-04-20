import LEDWall
import FFT
import SharedVariables
import threading
import sys
import time
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

shared_vars = SharedVariables.SharedVariables()

flaskApp = Flask(__name__)
flaskApi = Api(flaskApp)

colorParser = reqparse.RequestParser()
colorParser.add_argument('primaryColor', type=int, action='append')
colorParser.add_argument('secondaryColor', type=int, action='append')

settingsParser = reqparse.RequestParser()
settingsParser.add_argument('general', type=dict)
settingsParser.add_argument('color', type=dict)
settingsParser.add_argument('music', type=dict)
settingsParser.add_argument('strobo', type=dict)
settingsParser.add_argument('ambient', type=dict)

generalSettingsParser = reqparse.RequestParser()
generalSettingsParser.add_argument('brightness', type=float, location=('general',))

colorSettingsParser = reqparse.RequestParser()
colorSettingsParser.add_argument('primaryColor', type=dict, location=('color',))
colorSettingsParser.add_argument('secondaryColor', type=dict, location=('color',))

musicSettingsParser = reqparse.RequestParser()
musicSettingsParser.add_argument('fallingDot', type=bool, location=('music',))
musicSettingsParser.add_argument('dotSpeed', type=int, location=('music',))
musicSettingsParser.add_argument('fftWeightings', type=dict, location=('music',))

stroboSettingsParser = reqparse.RequestParser()
stroboSettingsParser.add_argument('frequency', type=float, location=('strobo',))
stroboSettingsParser.add_argument('dutyCycle', type=float, location=('strobo',))

ambientSettingsParser = reqparse.RequestParser()
ambientSettingsParser.add_argument('pulsing', type=bool, location=('ambient',))
ambientSettingsParser.add_argument('frequency', type=float, location=('ambient',))


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class Color(Resource):
    def options(self):
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        args = colorParser.parse_args()
        print(args)
        if args['primaryColor']:
            shared_vars.primaryColor = args['primaryColor']
        if args['secondaryColor']:
            shared_vars.secondaryColor = args['secondaryColor']
        return {'primaryColor': shared_vars.primaryColor, 'secondaryColor': shared_vars.secondaryColor}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}


flaskApi.add_resource(HelloWorld, '/')
flaskApi.add_resource(Color, '/color')


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
        t3 = threading.Thread(target=flaskApp.run, args=('192.168.120.13', 80,))
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
