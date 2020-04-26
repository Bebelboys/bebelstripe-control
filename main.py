import LEDWall
import FFT
import pong
import SharedVariables
import threading
import sys
import time
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import numpy as np

shared_vars = SharedVariables.SharedVariables()

ledwall = LEDWall.LEDWall()
fft = FFT.FFT()

flaskApp = Flask(__name__)
flaskApi = Api(flaskApp)

threads = []


def kill_threads():
    shared_vars.kill_threads = True
    for t in threads:
        t.join()
    threads.clear()
    shared_vars.kill_threads = False
    ledwall.show_color((0, 0, 0))


def change_mode():
    kill_threads()
    if shared_vars.on:
        if shared_vars.mode == 'music':
            t_music_spectrum = threading.Thread(
                target=ledwall.music_spectrum, args=(shared_vars,), daemon=True)
            t_music_spectrum.start()
            t_fft = threading.Thread(
                target=fft.start, args=(shared_vars,), daemon=True)
            t_fft.start()
            threads.append(t_music_spectrum)
            threads.append(t_fft)
        if shared_vars.mode == 'strobo':
            t_strobo = threading.Thread(
                target=ledwall.strobo, args=(shared_vars,), daemon=True)
            t_strobo.start()
            threads.append(t_strobo)
        if shared_vars.mode == 'pong':
            t_pong = threading.Thread(
                target=pong.main, args=(ledwall, shared_vars,), daemon=True)
            t_pong.start()
            threads.append(t_pong)


controlParser = reqparse.RequestParser()
controlParser.add_argument('on', type=bool)
controlParser.add_argument('mode', choices=('music', 'strobo', 'pong'))

settingsParser = reqparse.RequestParser()
settingsParser.add_argument('general', type=dict)
settingsParser.add_argument('color', type=dict)
settingsParser.add_argument('music', type=dict)
settingsParser.add_argument('strobo', type=dict)
settingsParser.add_argument('ambient', type=dict)

generalSettingsParser = reqparse.RequestParser()
generalSettingsParser.add_argument(
    'brightness', type=float, location=('general',))

colorSettingsParser = reqparse.RequestParser()
colorSettingsParser.add_argument(
    'primaryColor', type=int, location=('color',), action='append')
colorSettingsParser.add_argument(
    'secondaryColor', type=int, location=('color',), action='append')

musicSettingsParser = reqparse.RequestParser()
musicSettingsParser.add_argument('fallingDot', type=bool, location=('music',))
musicSettingsParser.add_argument(
    'fftWeightings', type=int, location=('music',), action='append')

stroboSettingsParser = reqparse.RequestParser()
stroboSettingsParser.add_argument(
    'frequency', type=float, location=('strobo',))
stroboSettingsParser.add_argument(
    'dutyCycle', type=float, location=('strobo',))

ambientSettingsParser = reqparse.RequestParser()
ambientSettingsParser.add_argument('pulsing', type=bool, location=('ambient',))
ambientSettingsParser.add_argument(
    'frequency', type=float, location=('ambient',))


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class Settings(Resource):
    def options(self):
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return shared_vars.list_settings(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        settings = settingsParser.parse_args()
        if settings['general'] is not None:
            general_settings = generalSettingsParser.parse_args(req=settings)
            if general_settings['brightness'] is not None:
                shared_vars.brightness = general_settings['brightness']
                # convert brightness scale [0-1] to LED brightness scale
                brightness_percent_to_led_brightness_in = [0, 0.5, 0.8, 1]
                brightness_percent_to_led_brightness_out = [0, 0.2, 0.5, 1]
                shared_vars.LEDBrightness = np.interp(
                    shared_vars.brightness, brightness_percent_to_led_brightness_in, brightness_percent_to_led_brightness_out)
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(
                    shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(
                    shared_vars.secondaryColor, shared_vars.LEDBrightness)
        if settings['color'] is not None:
            color_settings = colorSettingsParser.parse_args(req=settings)
            if color_settings['primaryColor'] is not None:
                shared_vars.primaryColor = color_settings['primaryColor']
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(
                    shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(
                    shared_vars.secondaryColor, shared_vars.LEDBrightness)
            if color_settings['secondaryColor'] is not None:
                shared_vars.secondaryColor = color_settings['secondaryColor']
                # apply brightness to LED color
                shared_vars.LEDPrimaryColor = ledwall.apply_brightness(
                    shared_vars.primaryColor, shared_vars.LEDBrightness)
                shared_vars.LEDSecondaryColor = ledwall.apply_brightness(
                    shared_vars.secondaryColor, shared_vars.LEDBrightness)
        if settings['music'] is not None:
            music_settings = musicSettingsParser.parse_args(req=settings)
            if music_settings['fallingDot'] is not None:
                shared_vars.fallingDot = music_settings['fallingDot']
            if music_settings['fftWeightings'] is not None:
                shared_vars.fftWeightings = music_settings['fftWeightings']
        if settings['strobo'] is not None:
            strobo_settings = stroboSettingsParser.parse_args(req=settings)
            if strobo_settings['frequency'] is not None:
                shared_vars.stroboFrequency = strobo_settings['frequency']
            if strobo_settings['dutyCycle'] is not None:
                shared_vars.stroboDutyCycle = strobo_settings['dutyCycle']
        if settings['ambient'] is not None:
            ambient_settings = ambientSettingsParser.parse_args(req=settings)
            if ambient_settings['pulsing'] is not None:
                shared_vars.ambientPulsing = ambient_settings['pulsing']
            if ambient_settings['frequency'] is not None:
                shared_vars.ambientFrequency = ambient_settings['frequency']
        return shared_vars.list_settings(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}


class Control(Resource):
    def options(self):
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return shared_vars.list_control(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        control = controlParser.parse_args()
        if control['on'] is not None:
            if shared_vars.on is not control['on']:
                shared_vars.on = control['on']
                if shared_vars.on:
                    change_mode()
                else:
                    kill_threads()
        if control['mode'] is not None:
            if shared_vars.mode is not control['mode']:
                shared_vars.mode = control['mode']
                change_mode()
        return shared_vars.list_control(), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}


flaskApi.add_resource(HelloWorld, '/')
flaskApi.add_resource(Settings, '/settings')
flaskApi.add_resource(Control, '/control')


def main():
    try:
        t_flask = threading.Thread(target=flaskApp.run, args=(
            '192.168.120.13', 80,), daemon=True)
        t_flask.start()

        ledwall.sinus(1)

        t_music_spectrum = threading.Thread(
            target=ledwall.music_spectrum, args=(shared_vars,), daemon=True)
        t_fft = threading.Thread(
            target=fft.start, args=(shared_vars,), daemon=True)
        t_music_spectrum.start()
        t_fft.start()
        threads.append(t_music_spectrum)
        threads.append(t_fft)

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
