import random
from enum import Enum

from LEDWall import LEDWall

import pdb

import time

# coordinate system starts at lower left LED

led_wall_width = LEDWall.num_columns
led_wall_height = LEDWall.num_rows

class InitialBallDirection(Enum):
    LEFT = 'initial_ball_direction_left'
    RIGHT = 'initial_ball_direction_right'

class PlayerPosition(Enum):
    LEFT = 'player_position_left'
    RIGHT = 'player_position_right'

class ScoredGoalByPlayer(Enum):
    LEFT = 'left_player_scored_goal'
    RIGHT = 'right_player_scored_goal'

class Ball:
    def __init__(self, initial_direction):
        self.color = (0, 128, 0)
        self.initBall(initial_direction)

    def initBall(self, initial_direction):
        self.position = [int(led_wall_width / 2), int(led_wall_height / 2)]

        if initial_direction == InitialBallDirection.LEFT:
            x_velocity = -1
        else:
            x_velocity = 1
        # y velocity can be +- 4, 3, 2, 1
        y_velocity = random.choice([i for i in range(-4, 5) if i not in [0]])
        self.velocity = [x_velocity, y_velocity]


    def updatePosition(self, left_paddle_y_position, left_paddle_height, right_paddle_y_position, right_paddle_height):
        new_x_position = self.position[0] + self.velocity[0]
        new_y_position = self.position[1] + self.velocity[1]

        # check if ball hits top or bottom wall and it needs to be reflected
        if new_y_position >= led_wall_height:
            new_y_position = led_wall_height
            self.velocity[1] = -self.velocity[1]
        elif new_y_position <= 0:
            new_y_position = 0
            self.velocity[1] = -self.velocity[1]

        # set new position of the ball
        self.position = [new_x_position, new_y_position]

        # check if ball hits paddle or it lands in the gutter
        if new_x_position == 0:
            if left_paddle_y_position <= new_y_position <= (left_paddle_y_position + left_paddle_height):
                # hit paddle, reflect ball
                self.velocity[0] = -self.velocity[0]
            else:
                # hit gutter, increment score for right player
                return ScoredGoalByPlayer.RIGHT

        elif new_x_position == led_wall_width - 1:
            if right_paddle_y_position <= new_y_position <= (right_paddle_y_position + right_paddle_height):
                # hit paddle, reflect ball
                self.velocity[0] = -self.velocity[0]
            else:
                # hit gutter, increment score for left player
                return ScoredGoalByPlayer.LEFT

class Paddle:
    def __init__(self, initial_x_position, initial_y_position):
        self.color = (0, 0, 128)
        self.height = 44 # DEBUGGING 8
        # coordinate system of paddle starts at lowest pixel of the paddle
        self.x_position = initial_x_position
        self.y_position = 0 # DEBUGGING initial_y_position #- int(self.height / 2) 
        self.y_velocity = 0
        

    def updatePosition(self):
        new_y_position = self.y_position + self.y_velocity
        # check if paddle is out of bounds with new position 
        if new_y_position < 0:
            new_y_position = 0
        elif (new_y_position + self.height - 1) > led_wall_height:
            new_y_position = new_y_position + self.height - 1

        self.y_position = new_y_position



class Player:
    def __init__(self, player_position):
        self.score = 0
        self.player_position = PlayerPosition

        paddle_initial_y_position = int(led_wall_height / 2)
        if self.player_position == PlayerPosition.LEFT:
            paddle_initial_x_position = 0 
        else:
            paddle_initial_x_position = led_wall_width 
        self.paddle = Paddle(paddle_initial_x_position, paddle_initial_y_position)

class Pong:
    def __init__(self):
        self.player_left = Player(PlayerPosition.LEFT)
        self.player_right = Player(PlayerPosition.RIGHT)
        self.ball = Ball(random.choice([InitialBallDirection.LEFT, InitialBallDirection.RIGHT]))
    
    def update(self):
        self.ball.updatePosition(self.player_left.paddle.y_position, self.player_left.paddle.height,
                                 self.player_right.paddle.y_position, self.player_right.paddle.height)



def main():
    led_wall = LEDWall()
    pong_game = Pong()

    while True:
        # delete everything
        led_wall.pixels.fill( (0, 0, 0) )
        # display left paddle
        #pdb.set_trace()
        for paddle_pixel in range(0, pong_game.player_left.paddle.height):
            led_wall.pixels[int(pong_game.player_left.paddle.y_position) + paddle_pixel] = pong_game.player_left.paddle.color
        # display right paddle
        for paddle_pixel in range(0, pong_game.player_right.paddle.height):
            led_wall.pixels[led_wall_height * (led_wall_width - 1) + int(pong_game.player_right.paddle.y_position) + paddle_pixel] = pong_game.player_right.paddle.color
        # display ball
        led_wall.pixels[led_wall_height * pong_game.ball.position[0] + pong_game.ball.position[1]] = pong_game.ball.color

        led_wall.pixels.show()

        # update game
        pong_game.update()
        time.sleep(.2)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception:
            pass
        