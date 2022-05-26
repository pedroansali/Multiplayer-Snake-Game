import pygame, sys, pickle
import random
from time import sleep

#Constantes
rows = 23
cols = 31
width = 800
height = 600
HEADERSIZE = 10

pygame.font.init()


class Border():
	def __init__(self, x, y, width, height, color):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.color = color
		self.rect = (x, y, width, height)

	def update(self):
		self.rect = (self.x, self.y, self.width, self.height)

	def draw(self, window):
		pygame.draw.rect(window, self.color, self.rect)


class Square():
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.color = (0, 255, 0)
		self.width = width
		self.height = height
		self.rect = (x, y, width, height)

	def update(self):
		self.rect = (self.x, self.y, self.width, self.height)

	def draw(self, window):
		pygame.draw.rect(window, self.color, self.rect)


class Screen():
	def __init__(self, rows, cols):
		self.rows = rows
		self.cols = cols

		self.make_screen()

	def make_screen(self):
		self.screen = [[0 for i in range(self.cols)] for j in range(self.rows)]


class Snake():
	def __init__(self, i, j, width, height, color, color_name, direction, g):
		self.score = 0
		self.dead = False
		self.moving = True
		self.i = i
		self.j = j
		self.width = width
		self.height = height
		self.color = color
		self.color_name = color_name
		self.g = g
		self.rect = (g.screen[i][j].x, g.screen[i][j].y, width, height)
		self.direction = direction
		self.speed = 1
		self.body = [] #corpo como uma lista vazia
		self.frame_count = 0
		self.frame_bound = 4

	def movement(self):
		if self.moving:
			keys = pygame.key.get_pressed()

			old_direction = self.direction

			# Mudando a direção da cobra (Left, Right, Up, Down)
			if keys[pygame.K_LEFT] and old_direction != 'R' and old_direction != 'L':
				self.direction = 'L'
			elif keys[pygame.K_RIGHT] and old_direction != 'L' and old_direction != 'R':
				self.direction = 'R'
			elif keys[pygame.K_UP] and old_direction != 'D' and old_direction != 'U':
				self.direction = 'U'
			elif keys[pygame.K_DOWN] and old_direction != 'U' and old_direction != 'D':
				self.direction = 'D'

			old_rect = self.rect

			# Movendo continuamente a cobra
			if self.direction == 'L':
				if self.frame_count >= self.frame_bound:
					if self.j == 0:
						self.collision()
						return
					else:
						self.j -= self.speed
						self.update(old_rect)
						self.frame_count = 0
				else:
					self.frame_count += 1
			elif self.direction == 'U':
				if self.frame_count >= self.frame_bound:
					if self.i == 0:
						self.collision()
						return
					else:
						self.i -= self.speed
						self.update(old_rect)
						self.frame_count = 0
				else:
					self.frame_count += 1
			elif self.direction == 'R':
				if self.frame_count >= self.frame_bound:
					if self.j == cols - 1:
						self.collision()
						return
					else:
						self.j += self.speed
						self.update(old_rect)
						self.frame_count = 0
				else:
					self.frame_count += 1
			else:
				if self.frame_count >= self.frame_bound:
					if self.i == rows - 1:
						self.collision()
						return
					else:
						self.i += self.speed
						self.update(old_rect)
						self.frame_count = 0
				else:
					self.frame_count += 1

	def update(self, old_rect):

		self.rect = (self.g.screen[self.i][self.j].x, self.g.screen[self.i][self.j].y, self.width, self.height)
		self.move_body(old_rect)

	def draw(self, window):
		pygame.draw.rect(window, self.color, self.rect)
		if self.direction == 'U':
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 4, self.rect[1] + 4, 4, 4))
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 12, self.rect[1] + 4, 4, 4))
		elif self.direction == 'R':
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 12, self.rect[1] + 4, 4, 4))
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 12, self.rect[1] + 12, 4, 4))
		elif self.direction == 'D':
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 4, self.rect[1] + 12, 4, 4))
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 12, self.rect[1] + 12, 4, 4))
		else:
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 4, self.rect[1] + 4, 4, 4))
			pygame.draw.rect(window, (255, 255, 255), (self.rect[0] + 4, self.rect[1] + 12, 4, 4))
		for i in self.body:
			pygame.draw.rect(window, self.color, i)

	def verify_collision(self, a, eat_sound, s2):

		# Verificando com outra snake
		if self.i == s2.i and self.j == s2.j:
			pass
		else:
			for b in s2.body:
				if b[0] == self.rect[0] and b[1] == self.rect[1]:
					self.collision()
				else:
					pass

		# Verificando com a maçã
		if a.i == self.i and a.j == self.j:
			a.visible = False
			self.score += 1
			a.eaten(eat_sound)
			self.growth()
			a.change_pos(self.g)
			a.visible = True
			return True
		else:
			return False

	def collision(self):

		self.moving = False
		self.dead = True

	def growth(self):
		self.body.append(self.rect) #acrescenta um no corpo

	def move_body(self, old_rect):
		if self.body:
			for i in range(len(self.body) - 1, 0, -1):
				self.body[i] = self.body[i - 1]
			self.body[0] = old_rect


class Apple():
	def __init__(self, g):
		self.visible = True
		self.width = 24
		self.height = 24
		self.color = (255, 0, 0)
		self.rect = (0, 0, 20, 20)
		self.g = g
		self.square = 0
		self.image = None
		self.change_pos(self.g)

	def update(self):
		self.rect = (self.x, self.y,)

	def draw(self, window, image_surface):
		if self.visible:
			self.update()
			window.blit(image_surface, self.rect)

	def change_pos(self, g):
		self.i = random.randint(0, rows - 1)
		self.j = random.randint(0, cols - 1)
		self.cell = g.screen[self.i][self.j]
		self.x = self.cell.x
		self.y = self.cell.y
		self.update()

	def eaten(self, eat_sound):
		eat_sound.play()


class Game:
	def __init__(self, id):
		self.ready = False
		self.id = id
		self.snakes = [0, 0]
		self.alive = [True, True]
		self.a = None
		self.g = None

	def connected(self):
		return self.ready


def encode(data, mode):
	if mode == "pickle":
		data = pickle.dumps(data)
		data = bytes(f"{len(data):<{HEADERSIZE}}", "utf-8") + data
		return data

	elif mode == "string":
		data = bytes(f"{len(data):<{HEADERSIZE}}" + data, "utf-8")
		return data

def receive_decode(conn, mode):
	if mode == "pickle":
		#cria uma string de bytes
		full_msg = b""
		new_msg = True

		while True:

			try:
				msg = conn.recv(4096) #capacidade da msg
			except Exception as e:
				print(e)
			if new_msg:
				try:
					msglen = int(msg[:HEADERSIZE])
				except:
					return -1
				new_msg = False

			full_msg += msg

			if len(full_msg) - HEADERSIZE == msglen:
				return pickle.loads(full_msg[HEADERSIZE:])


	elif mode == "string":
		full_msg = b""
		new_msg = True

		while True:
			msg = conn.recv(4096)
			if new_msg:
				msglen = msg[:HEADERSIZE]
				new_msg = False

			full_msg += msg

			if len(full_msg) - HEADERSIZE == msglen:
				return full_msg[HEADERSIZE:].decode("utf-8")


class GameOver():
	def __init__(self, won, msg, s1, s2):
		self.won = won
		self.msg = msg
		self.s1 = s1
		self.s2 = s2
		if self.won:
			# Vitória
			self.t = Text("Parabéns. Você Ganhou!!!!", (0, 128, 0), 35, height / 2 - 100)

		else:
			# Derrota
			self.t = Text("Que pena... Você perdeu!!!!", (255, 0, 0), 35, height / 2 - 100)

		self.score = Text("Seu placar:" + str(s1.score) + "    " + "Placar do oponente:" + str(s2.score), (0, 0, 0), 35,
						  height / 2)
		self.press_enter = Text("Pressione Enter para jogar novamente", (0, 128, 0), 35, height / 2 + 100)

	def draw(self, window):
		window.fill((255, 255, 255))
		self.t.draw(window)
		self.score.draw(window)
		self.press_enter.draw(window)

		pygame.display.update()

	def wait_key(self, window):

		draw_end = True
		while draw_end:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					menu_run = False
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						print("Fechando...")
						draw_end = False
						break

			self.draw(window)


class Text():
	def __init__(self, text, color, size, y_shift):
		self.text = text
		self.color = color
		self.size = size
		self.y_shift = y_shift
		self.font = pygame.font.SysFont("Verdana", self.size, False, True)
		self.screen_text = self.font.render(self.text, True, self.color)
		self.rect = self.screen_text.get_rect()
		self.x = round(width / 2) - round(self.rect.width / 2)
		self.y = self.y_shift
		self.width = self.rect.width
		self.height = self.rect.height
		self.display = True

	def draw(self, window):
		if self.display:
			window.blit(self.screen_text, (self.x, self.y))	