import LEDWall
import FFT
import SharedVariables
import threading
import sys
import time
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import math

shared_vars = SharedVariables.SharedVariables()

ledwall = LEDWall.LEDWall()
fft = FFT.FFT()

flaskApp = Flask(__name__)
flaskApi = Api(flaskApp)

colorParser = reqparse.RequestParser()
colorParser.add_argument('primaryColor', type=int, action='append')
colorParser.add_argument('secondaryColor', type=int, action='append')

controlParser = reqparse.RequestParser()
controlParser.add_argument('on', type=bool)
controlParser.add_argument('mode', type=int)

settingsParser = reqparse.RequestParser()
settingsParser.add_argument('general', type=dict)
settingsParser.add_argument('color', type=dict)
settingsParser.add_argument('music', type=dict)
settingsParser.add_argument('strobo', type=dict)
settingsParser.add_argument('ambient', type=dict)

generalSettingsParser = reqparse.RequestParser()
generalSettingsParser.add_argument('brightness', type=float, location=('general',))

colorSettingsParser = reqparse.RequestParser()
colorSettingsParser.add_argument('primaryColor', type=int, location=('color',), action='append')
colorSettingsParser.add_argument('secondaryColor', type=int, location=('color',), action='append')

musicSettingsParser = reqparse.RequestParser()
musicSettingsParser.add_argument('fallingDot', type=bool, location=('music',))
musicSettingsParser.add_argument('dotSpeed', type=int, location=('music',))
musicSettingsParser.add_argument('fftWeightings', type=int, location=('music',), action='append')

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


class Settings(Resource):
    def options(self):
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return shared_vars.list_settings(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        settings = settingsParser.parse_args()
        if settings['general']:
            general_settings = generalSettingsParser.parse_args(req=settings)
            if general_settings['brightness']:
                shared_vars.brightness = general_settings['brightness']
                # convert brightness scale [0-1] to LED brightness scale
                shared_vars.LEDBrightness = 2.2405 * math.pow(shared_vars.brightness, 3) - 2.1518 * math.pow(shared_vars.brightness, 2) + 0.9068 * shared_vars.brightness + 0.0045
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(shared_vars.secondaryColor, shared_vars.LEDBrightness)
        if settings['color']:
            color_settings = colorSettingsParser.parse_args(req=settings)
            if color_settings['primaryColor']:
                shared_vars.primaryColor = color_settings['primaryColor']
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(shared_vars.secondaryColor, shared_vars.LEDBrightness)
            if color_settings['secondaryColor']:
                shared_vars.secondaryColor = color_settings['secondaryColor']
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(shared_vars.secondaryColor, shared_vars.LEDBrightness)
        if settings['music']:
            music_settings = musicSettingsParser.parse_args(req=settings)
            if music_settings['fallingDot']:
                shared_vars.fallingDot = music_settings['fallingDot']
            if music_settings['dotSpeed']:
                shared_vars.dotSpeed = music_settings['dotSpeed']
            if music_settings['fftWeightings']:
                shared_vars.fftWeightings = music_settings['fftWeightings']
        if settings['strobo']:
            strobo_settings = stroboSettingsParser.parse_args(req=settings)
            if strobo_settings['frequency']:
                shared_vars.stroboFrequency = strobo_settings['frequency']
            if strobo_settings['dutyCycle']:
                shared_vars.stroboDutyCycle = strobo_settings['dutyCycle']
        if settings['ambient']:
            ambient_settings = ambientSettingsParser.parse_args(req=settings)
            if ambient_settings['pulsing']:
                shared_vars.ambientPulsing = ambient_settings['pulsing']
            if ambient_settings['frequency']:
                shared_vars.ambientFrequency = ambient_settings['frequency']
        return shared_vars.list_settings(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}


class Control(Resource):
    def options(self):
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return shared_vars.list_control(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        control = controlParser.parse_args()
        if control['on']:
            shared_vars.on = control['on']
        if control['mode']:
            shared_vars.mode = control['mode']
        return shared_vars.list_control(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}


flaskApi.add_resource(HelloWorld, '/')
flaskApi.add_resource(Color, '/color')
flaskApi.add_resource(Settings, '/settings')
flaskApi.add_resource(Control, '/control')


def main():
    try:
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
