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

        if pong_control_arguments['left_player'] is not None:
            paddle_velocity = pong_control_arguments['left_player']['paddle']['y_velocity']
            if paddle_velocity == 1:
                self.pong_game.left_player.paddle.startUpwardMovement()
            elif paddle_velocity == 0:
                self.pong_game.left_player.paddle.stopMovement()
            elif paddle_velocity == -1:
                self.pong_game.left_player.paddle.startDownwardMovement()
            else:
                raise Exception(
                    f'Invalid paddle velocity given to pong control: {paddle_velocity}')

        if pong_control_arguments['right_player'] is not None:
            paddle_velocity = pong_control_arguments['right_player']['paddle']['y_velocity']
            print(paddle_velocity, type(paddle_velocity))
            if paddle_velocity == 1:
                print('hi')
                self.pong_game.right_player.paddle.startUpwardMovement()
            elif paddle_velocity == 0:
                self.pong_game.right_player.paddle.stopMovement()
            elif paddle_velocity == -1:
                self.pong_game.right_player.paddle.startDownwardMovement()
            else:
                raise Exception(
                    f'Invalid paddle velocity given to pong control: {paddle_velocity}')

        # new_player_state = self.pong_game.getPlayerState(
        #     pong.PlayerPosition.LEFT if player_id == 'left_player' else pong.PlayerPosition.RIGHT)

        return json.loads(self.pong_game.getGameState()), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
