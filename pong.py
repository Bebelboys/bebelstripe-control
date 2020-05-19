import random
from enum import Enum
import time
import keyboard
import json

from LEDWall import LEDWall


def jsonDumpsDefault(x):
    if isinstance(x, Enum):
        return x._value_  # _value_ oder _name_
    else:
        return getattr(x, '__dict__', str(x))

# coordinate system starts at lower left LED


led_wall_width = LEDWall.num_columns
led_wall_height = LEDWall.num_rows


class InitialBallDirection(Enum):
    LEFT = 'initial_ball_direction_left'
    RIGHT = 'initial_ball_direction_right'


class PlayerPosition(Enum):
    LEFT = 'left_player'
    RIGHT = 'right_player'


class ScoredGoalByPlayer(Enum):
    LEFT = 'left_player_scored_goal'
    RIGHT = 'right_player_scored_goal'


class BallReflectedBy(Enum):
    LEFT_PADDLE = 'ball_reflected_by_left_paddle'
    RIGHT_PADDLE = 'ball_reflected_by_right_paddle'


class Ball:
    normal_color = (0, 128, 0)
    score_color = (128, 0, 0)

    def __init__(self, initial_direction):
        self.color = Ball.normal_color
        self.initBall(initial_direction)

    def setNormalColor(self):
        self.color = Ball.normal_color

    def setScoreColor(self):
        self.color = Ball.score_color

    def initBall(self, initial_direction=None):
        self.setNormalColor()
        self.position = [int(led_wall_width / 2), int(led_wall_height / 2)]

        if initial_direction is None:
            random.choice([InitialBallDirection.LEFT,
                           InitialBallDirection.RIGHT])
        if initial_direction == InitialBallDirection.LEFT:
            x_velocity = -1
        elif initial_direction == InitialBallDirection.RIGHT:
            x_velocity = 1
        else:
            raise Exception('Invalid initial_direction (Ball.initBall)')

        # y velocity can be +- 4, 3, 2, 1
        # DEBUGGING random.choice([i for i in range(-4, 5) if i not in [0]])
        y_velocity = 0
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
            if left_paddle_y_position <= new_y_position <= (left_paddle_y_position + left_paddle_height - 1):
                # hit paddle, reflect ball
                self.velocity[0] = -self.velocity[0]
                self.velocity[1] = random.choice(
                    [i for i in range(-4, 5) if i not in [0]])
                return BallReflectedBy.LEFT_PADDLE

        elif new_x_position == led_wall_width - 1:
            if right_paddle_y_position <= new_y_position <= (right_paddle_y_position + right_paddle_height - 1):
                # hit paddle, reflect ball
                self.velocity[0] = -self.velocity[0]
                self.velocity[1] = random.choice(
                    [i for i in range(-4, 5) if i not in [0]])
                return BallReflectedBy.RIGHT_PADDLE

        if new_x_position <= 0:
            # hit gutter, increment score for right player
            self.setScoreColor()
            return ScoredGoalByPlayer.RIGHT
        elif (new_x_position >= (led_wall_width - 1)):
            # hit gutter, increment score for left player
            self.setScoreColor()
            return ScoredGoalByPlayer.LEFT


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

    def startUpwardMovement(self):
        self.y_velocity = 1

    def startDownwardMovement(self):
        self.y_velocity = -1

    def stopMovement(self):
        self.y_velocity = 0

    def setHeight(self, height):
        self.height = height


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
    def __init__(self, ball_updating_frequency_hz=4):
        self.left_player = Player(PlayerPosition.LEFT)
        self.right_player = Player(PlayerPosition.RIGHT)
        self.ball = Ball(random.choice(
            [InitialBallDirection.LEFT, InitialBallDirection.RIGHT]))

        self.last_ball_update_time = time.time()
        self.original_ball_updating_frequency_hz = ball_updating_frequency_hz
        self.ball_updating_frequency_hz = ball_updating_frequency_hz
        self.ball_updating_pause_s = 0
        self.initialize_ball = False
        self.initial_ball_direction = None

    def update(self):
        self.left_player.paddle.updatePosition()
        self.right_player.paddle.updatePosition()

        # ball is updated with a lower frequency than the paddles so the paddles can move more smoothly
        if (time.time() - self.last_ball_update_time) > (1/self.ball_updating_frequency_hz + self.ball_updating_pause_s):
            self.ball_updating_pause_s = 0
            self.last_ball_update_time = time.time()

            if self.initialize_ball:
                self.ball.initBall(self.initial_ball_direction)
                self.initialize_ball = False
            else:
                result = self.ball.updatePosition(self.left_player.paddle.y_position, self.left_player.paddle.height,
                                                  self.right_player.paddle.y_position, self.right_player.paddle.height)
                if(result == ScoredGoalByPlayer.LEFT):
                    self.left_player.score += 1
                    self.initial_ball_direction = InitialBallDirection.LEFT
                    self.initialize_ball = True
                    self.resetBallUpdatingFrequency()
                    return result
                elif(result == ScoredGoalByPlayer.RIGHT):
                    self.right_player.score += 1
                    self.initial_ball_direction = InitialBallDirection.RIGHT
                    self.initialize_ball = True
                    self.resetBallUpdatingFrequency()
                    return result
                elif (result == BallReflectedBy.LEFT_PADDLE or result == BallReflectedBy.RIGHT_PADDLE):
                    self.increaseBallUpdatingFrequency()

        return None

    def delayBallUpdate(self, delay_s):
        self.ball_updating_pause_s = delay_s

    def increaseBallUpdatingFrequency(self, factor=1.05):
        self.ball_updating_frequency_hz *= factor

    def resetBallUpdatingFrequency(self):
        self.ball_updating_frequency_hz = self.original_ball_updating_frequency_hz

    def getPlayerState(self, player_id):
        if player_id == PlayerPosition.LEFT:
            return json.dumps(self.left_player, default=jsonDumpsDefault, sort_keys=True)
        elif player_id == PlayerPosition.RIGHT:
            return json.dumps(self.right_player, default=jsonDumpsDefault, sort_keys=True)
        else:
            raise Exception(
                f'Invalid player_id: {player_id} in Pong.getPlayerState')

    def getGameState(self):
        return json.dumps(self.__dict__, default=jsonDumpsDefault, sort_keys=True)

    def restartGame(self):
        original_ball_updating_frequency_hz = self.original_ball_updating_frequency_hz
        del self.__dict__
        self.__init__(original_ball_updating_frequency_hz)


def refreshGameScreen(led_wall, pong_game):
    # delete everything
    led_wall.pixels.fill((0, 0, 0))
    # display left paddle
    for paddle_pixel in range(0, pong_game.left_player.paddle.height):
        led_wall.pixels[int(pong_game.left_player.paddle.y_position) +
                        paddle_pixel] = pong_game.left_player.paddle.color
    # display right paddle
    for paddle_pixel in range(0, pong_game.right_player.paddle.height):
        led_wall.pixels[led_wall_height * (led_wall_width - 1) + int(
            pong_game.right_player.paddle.y_position) + paddle_pixel] = pong_game.right_player.paddle.color
    # display left player score
    for score_pixel in range(0, pong_game.left_player.score):
        led_wall.pixels[led_wall_height *
                        int(led_wall_width / 2 - 1) + led_wall_height - score_pixel - 1] = (255, 0, 0)
    # display right player score
    for score_pixel in range(0, pong_game.right_player.score):
        led_wall.pixels[led_wall_height *
                        int(led_wall_width / 2) + led_wall_height - score_pixel - 1] = (255, 0, 0)
    # display ball
    led_wall.pixels[led_wall_height * pong_game.ball.position[0] +
                    pong_game.ball.position[1]] = pong_game.ball.color

    led_wall.pixels.show()


def main(pong_game, led_wall, shared_vars):
    keyboard.on_press_key(
        'w', lambda _: pong_game.left_player.paddle.startUpwardMovement())
    keyboard.on_release_key(
        'w', lambda _: pong_game.left_player.paddle.stopMovement())
    keyboard.on_press_key(
        's', lambda _: pong_game.left_player.paddle.startDownwardMovement())
    keyboard.on_release_key(
        's', lambda _: pong_game.left_player.paddle.stopMovement())

    keyboard.on_press_key(
        'up', lambda _: pong_game.right_player.paddle.startUpwardMovement())
    keyboard.on_release_key(
        'up', lambda _: pong_game.right_player.paddle.stopMovement())
    keyboard.on_press_key(
        'down', lambda _: pong_game.right_player.paddle.startDownwardMovement())
    keyboard.on_release_key(
        'down', lambda _: pong_game.right_player.paddle.stopMovement())

    pause_game_due_to_new_ball_init = True

    while not shared_vars.kill_threads:
        # pause if ball was freshly initialized or a goal was just scored
        if pause_game_due_to_new_ball_init:
            pong_game.delayBallUpdate(1)
            pause_game_due_to_new_ball_init = False

        refreshGameScreen(led_wall, pong_game)

        # update game
        result = pong_game.update()
        if result is not None:
            # goal was scored
            pause_game_due_to_new_ball_init = True


if __name__ == '__main__':
    led_wall = LEDWall()

    class MockSharedVars:
        kill_threads = False

    mock_shared_vars = MockSharedVars()
    while True:
        try:
            main(led_wall, mock_shared_vars)
        except Exception as e:
            print(e)
