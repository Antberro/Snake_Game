import tkinter as tk
from tkinter import messagebox
import time
import random

class Constants:
	# time
	TIME_STEP = 0.15

	# canvas info
	WIDTH = 400
	HEIGHT = 400
	BACKGROUND_COLOR = 'black'

	# snake info
	SNAKE_POSITION = (250, 250)
	SNAKE_SIZE = (20, 20)
	SNAKE_COLOR = 'green'
	SNAKE_SPEED = 20

	# snack info
	SNACK_POSITION = (70, 70)
	SNACK_SIZE = (20, 20)
	SNACK_COLOR = 'red'


class Display:
	def __init__(self):
		"""
		Object that creates window and canvas to display objects.
		"""
		self.settings = {
			'bg': Constants.BACKGROUND_COLOR,
			'width': Constants.WIDTH,
			'height': Constants.HEIGHT
		}
		self.key = None
		self.root = tk.Tk()  # main root tkinter object
		self.root.title('Snake Game')
		self.canvas = tk.Canvas(self.root, self.settings)  # main canvas tkinter object
		self.canvas.pack()

	def draw(self, render_dict):
		"""
		Given render_dict containing game data, plots all blocks on canvas.
		"""
		# clear canvas
		self.canvas.delete('all')

		# draw snake on canvas
		snake_blocks = render_dict['snake_blocks']
		for block in snake_blocks:
			x, y = block.position
			w, h = Constants.SNAKE_SIZE
			self.canvas.create_rectangle(x - w/2, y - h/2, x + w/2, y + h/2, outline=Constants.SNAKE_COLOR, fill=Constants.SNAKE_COLOR)
			self.canvas.pack()

		# draw snack on canvas
		x, y = render_dict['snack_block'].position
		w, h = Constants.SNACK_SIZE
		self.canvas.create_rectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2, outline=Constants.SNACK_COLOR, fill=Constants.SNACK_COLOR)
		self.canvas.pack()

		# update canvas
		self.canvas.update()

	def show(self):
		"""
		Opens window with canvas.
		"""
		self.root.mainloop()


class Game:
	def __init__(self, game_info):
		"""
		Creates game object that runs game.
		"""
		# deserialize game info
		self.snake_blocks = game_info['snake_blocks']
		self.snack_block = game_info['snack_block']
		self.snake_length = game_info['snake_length']
		self.snake_direction = game_info['direction']
		self.status = 'ongoing'

	def render(self):
		"""
		Serializes game info into a dictionary. Used to create
		new instance of Game object.
		"""
		output = {
			'snake_blocks': self.snake_blocks,
			'snack_block': self.snack_block,
			'snake_length': self.snake_length,
			'direction': self.snake_direction
		}
		return output

	def timestep(self, key_press=None):
		"""
		Make all changes necessary to move the
		game forward one timestep. Does the following:
			1) compute front position of snake given key_press and update direction
			2) check if snake is out of bounds
			3) check if snake intersects itself
			4) if snake ate snack change position of snack and extend snake
		"""
		# 1) update position of snake according to key press
		x, y = self.snake_blocks[0].position  # get current head position
		if key_press is None:  # keep going in current direction
			if self.snake_direction == 'N': new_position = (x, y - Constants.SNAKE_SPEED)
			elif self.snake_direction == 'S': new_position = (x, y + Constants.SNAKE_SPEED)
			elif self.snake_direction == 'E': new_position = (x + Constants.SNAKE_SPEED, y)
			elif self.snake_direction == 'W': new_position = (x - Constants.SNAKE_SPEED, y)
		elif key_press == 'left':  # go left
			self.snake_direction = 'W'
			new_position = (x - Constants.SNAKE_SPEED, y)
		elif key_press == 'right':  # go right
			self.snake_direction = 'E'
			new_position = (x + Constants.SNAKE_SPEED, y)
		elif key_press == 'up':  # go up
			self.snake_direction = 'N'
			new_position = (x, y - Constants.SNAKE_SPEED)
		elif key_press == 'down':  # go down
			self.snake_direction = 'S'
			new_position = (x, y + Constants.SNAKE_SPEED)

		# add new snake block at the front
		self.snake_blocks.insert(0, Block(new_position, Constants.SNAKE_SIZE))

		# 2) check if snake is out of bounds
		if not self.snake_blocks[0].on_board():
			self.status = 'defeat'

		# 3) check if snake collides with itself
		for block in self.snake_blocks[1:-1]:
			if self.snake_blocks[0].collides_with(block):
				self.status = 'defeat'

		# 4) check if snake ate snack
		if self.snake_blocks[0].collides_with(self.snack_block):
			# remove snack and spawn new snack at valid location
			new_x = random.randint(0 + Constants.SNACK_SIZE[0] / 2, Constants.WIDTH - Constants.SNACK_SIZE[0] / 2)
			new_y = random.randint(0 + Constants.SNACK_SIZE[1] / 2, Constants.HEIGHT - Constants.SNACK_SIZE[1] / 2)
			self.snack_block = Block((new_x, new_y), Constants.SNAKE_SIZE)
			self.snake_length += 1
		else:
			# remove block at end of snake
			del self.snake_blocks[-1]


class Block:
	def __init__(self, position, size):
		"""
		Block object that represents snake segments and snack block.
		"""
		self.position = position
		self.size = size

	def on_board(self):
		"""
		Determines if block is on the game board.
		Returns True if on board, otherwise False.
		"""
		x, y = self.position
		w, h = self.size
		x_in_bounds = 0 <= x - w/2 and x + w/2 <= Constants.WIDTH
		y_in_bounds = 0 <= y - h/2 and y + h/2 <= Constants.HEIGHT
		if x_in_bounds and y_in_bounds:
			return True
		else:
			return False

	def collides_with(self, other):
		"""
		Determines if block collides with other block.
		Returns True of blocks collide, otherwise return
		False.
		"""
		# position and size of self
		x, y = self.position
		width, height = self.size

		# position and size of other block
		other_x, other_y = other.position
		other_width, other_height = other.size

		# collision detection
		x_dist, y_dist = abs(x - other_x), abs(y - other_y)
		x_overlap = x_dist < (width + other_width) / 2
		y_overlap = y_dist < (height + other_height) / 2
		if x_overlap and y_overlap:
			return True
		else:
			return False


def play():
	"""
	Play through a round of game.
	"""
	default_game_info = {
		'snake_blocks': [Block((0.8 * Constants.WIDTH, 0.8 * Constants.HEIGHT), Constants.SNAKE_SIZE)],
		'snack_block': Block((0.2 * Constants.WIDTH, 0.2 * Constants.HEIGHT), Constants.SNACK_SIZE),
		'snake_length': 1,
		'direction': 'N'
	}

	window = Display()  # create game window instance
	game = Game(default_game_info)  # create game instance

	def press_left(event): window.key = 'left'
	def press_right(event): window.key = 'right'
	def press_up(event): window.key = 'up'
	def press_down(event): window.key = 'down'

	window.root.bind('<Left>', press_left)
	window.root.bind('<Right>', press_right)
	window.root.bind('<Up>', press_up)
	window.root.bind('<Down>', press_down)

	# begin game loop
	game_info = default_game_info
	while game.status == 'ongoing':
		# move game forward by one timestep
		game = Game(game_info)
		game.timestep(window.key)
		window.key = None

		# render and draw
		new_game_info = game.render()
		window.draw(new_game_info)
		game_info = new_game_info

		# wait
		time.sleep(Constants.TIME_STEP)

	play_again = messagebox.askyesno('Game Over', 'Total length: {}\nPlay Again?'.format(game.snake_length))
	
	window.root.destroy()

	# display window
	window.show()
	return play_again


if __name__ == '__main__':
	while True:
		play_again = play()
		if not play_again:
			break
