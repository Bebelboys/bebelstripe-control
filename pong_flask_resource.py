from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json

import pong


pong_control_parser = reqparse.RequestParser()
pong_control_parser.add_argument('left_player', type=dict)
pong_control_parser.add_argument('right_player', type=dict)

# pong_control_parser.add_argument('player_state', type=dict)


class PongControl(Resource):
    def __init__(self, pong_game):
        self.pong_game = pong_game

    def options(self):
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'PUT, GET, OPTIONS', 'Access-Control-Allow-Headers': '*'}

    def get(self):
        return json.loads(self.pong_game.getGameState()), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}

    def put(self):
        pong_control_arguments = pong_control_parser.parse_args()

        # check which players should be modified
        players_to_modify = dict()
        if pong_control_arguments['left_player'] is not None:
            players_to_modify.update(
                {'left_player': self.pong_game.left_player})
        if pong_control_arguments['right_player'] is not None:
            players_to_modify.update(
                {'right_player': self.pong_game.right_player})

        for player_string, player_object in players_to_modify.items():
            player_paddle_arguments = pong_control_arguments[player_string]['paddle']

            if 'y_velocity' in player_paddle_arguments:
                paddle_velocity = player_paddle_arguments['y_velocity']
                if paddle_velocity == 1:
                    player_object.paddle.startUpwardMovement()
                elif paddle_velocity == 0:
                    player_object.paddle.stopMovement()
                elif paddle_velocity == -1:
                    player_object.paddle.startDownwardMovement()
                else:
                    raise Exception(
                        f'Invalid paddle velocity given to pong control: {player_string} {paddle_velocity}')

            if 'height' in player_paddle_arguments:
                paddle_height = player_paddle_arguments['height']
                player_object.paddle.setHeight(paddle_height)

        # new_player_state = self.pong_game.getPlayerState(
        #     pong.PlayerPosition.LEFT if player_id == 'left_player' else pong.PlayerPosition.RIGHT)

        return json.loads(self.pong_game.getGameState()), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
