import random
from enum import Enum
import keyboard

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
            new_y_position = led_wall_height - 1
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
                self.velocity[1] = random.choice(
                    [i for i in range(-4, 5) if i not in [0]])

        elif new_x_position == led_wall_width - 1:
            if right_paddle_y_position <= new_y_position <= (right_paddle_y_position + right_paddle_height):
                # hit paddle, reflect ball
                self.velocity[0] = -self.velocity[0]
                self.velocity[1] = random.choice(
                    [i for i in range(-4, 5) if i not in [0]])

        elif new_x_position < 0:
            # hit gutter, increment score for right player
            return ScoredGoalByPlayer.RIGHT
        elif new_x_position >= led_wall_width:
            # hit gutter, increment score for left player
            return ScoredGoalByPlayer.LEFT


# class PaddleMovementDirection(Enum):
#     UP = 'paddle_movement_direction_up'
#     DOWN = 'paddle_movement_direction_down'
#     STOP = 'paddle_movement_direction_stop'


class Paddle:
    def __init__(self, initial_x_position, initial_y_position, height=8):
        self.color = (0, 0, 128)
        self.height = height
        # coordinate system of paddle starts at lowest pixel of the paddle
        self.x_position = initial_x_position
        self.y_position = initial_y_position
        self.y_velocity = 0

    def updatePosition(self):
        new_y_position = self.y_position + self.y_velocity
        # check if paddle is out of bounds with new position
        if new_y_position < 0:
            new_y_position = 0
        elif new_y_position > (led_wall_height - self.height):
            new_y_position = led_wall_height - self.height

        self.y_position = new_y_position

    # def movePaddle(self, direction):
    #     if (direction == PaddleMovementDirection.UP):
    #         self.y_velocity = int(self.height/2)
    #     elif (direction == PaddleMovementDirection.DOWN):
    #         self.y_velocity = -int(self.height/2)
    #     elif (direction == PaddleMovementDirection.STOP):
    #         self.y_velocity = 0

    def movePaddleUp(self):
        self.y_velocity = 1

    def movePaddleDown(self):
        self.y_velocity = -1

    def stopPaddle(self):
        self.y_velocity = 0


class Player:
    def __init__(self, player_position):
        self.score = 0
        self.player_position = player_position

        paddle_height = 8
        paddle_initial_y_position = int(
            led_wall_height / 2) - int(paddle_height / 2)
        if self.player_position == PlayerPosition.LEFT:
            paddle_initial_x_position = 0
        elif self.player_position == PlayerPosition.RIGHT:
            paddle_initial_x_position = led_wall_width

        self.paddle = Paddle(paddle_initial_x_position,
                             paddle_initial_y_position, paddle_height)


class Pong:
    def __init__(self, ball_updating_frequency_hz=1):
        self.player_left = Player(PlayerPosition.LEFT)
        self.player_right = Player(PlayerPosition.RIGHT)
        self.ball = Ball(random.choice(
            [InitialBallDirection.LEFT, InitialBallDirection.RIGHT]))

        self.last_ball_update_time = time.time()
        self.ball_updating_frequency_hz = ball_updating_frequency_hz

    def update(self):
        self.player_left.paddle.updatePosition()
        self.player_right.paddle.updatePosition()
        if (time.time() - self.last_ball_update_time) > 1/self.ball_updating_frequency_hz:
            self.last_ball_update_time = time.time()
            result = self.ball.updatePosition(self.player_left.paddle.y_position, self.player_left.paddle.height,
                                              self.player_right.paddle.y_position, self.player_right.paddle.height)

            if(result == ScoredGoalByPlayer.LEFT):
                self.player_left.score += 1
                time.sleep(1)
                self.ball.initBall(InitialBallDirection.LEFT)
            elif(result == ScoredGoalByPlayer.RIGHT):
                self.player_right.score += 1
                time.sleep(1)
                self.ball.initBall(InitialBallDirection.RIGHT)


def main():
    led_wall = LEDWall()
    pong_game = Pong(ball_updating_frequency_hz=4)

    keyboard.on_press_key(
        'w', lambda _: pong_game.player_left.paddle.movePaddleUp())
    keyboard.on_release_key(
        'w', lambda _: pong_game.player_left.paddle.stopPaddle())
    keyboard.on_press_key(
        's', lambda _: pong_game.player_left.paddle.movePaddleDown())
    keyboard.on_release_key(
        's', lambda _: pong_game.player_left.paddle.stopPaddle())

    keyboard.on_press_key(
        'up', lambda _: pong_game.player_right.paddle.movePaddleUp())
    keyboard.on_release_key(
        'up', lambda _: pong_game.player_right.paddle.stopPaddle())
    keyboard.on_press_key(
        'down', lambda _: pong_game.player_right.paddle.movePaddleDown())
    keyboard.on_release_key(
        'down', lambda _: pong_game.player_right.paddle.stopPaddle())

    while True:
        # delete everything
        led_wall.pixels.fill((0, 0, 0))
        # display left paddle
        for paddle_pixel in range(0, pong_game.player_left.paddle.height):
            led_wall.pixels[int(pong_game.player_left.paddle.y_position) +
                            paddle_pixel] = pong_game.player_left.paddle.color
        # display right paddle
        for paddle_pixel in range(0, pong_game.player_right.paddle.height):
            led_wall.pixels[led_wall_height * (led_wall_width - 1) + int(
                pong_game.player_right.paddle.y_position) + paddle_pixel] = pong_game.player_right.paddle.color
        # display left player score
        for score_pixel in range(0, pong_game.player_left.score):
            led_wall.pixels[led_wall_height *
                            int(led_wall_width / 2 - 1) + led_wall_height - score_pixel - 1] = (255, 0, 0)
        # display right player score
        for score_pixel in range(0, pong_game.player_right.score):
            led_wall.pixels[led_wall_height *
                            int(led_wall_width / 2) + led_wall_height - score_pixel - 1] = (255, 0, 0)
        # display ball
        led_wall.pixels[led_wall_height * pong_game.ball.position[0] +
                        pong_game.ball.position[1]] = pong_game.ball.color

        led_wall.pixels.show()

        # update game
        pong_game.update()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception:
            pass
