import pygame, sys
import random
from components import *
from connection import *
from time import sleep 

#Constantes
rows = 23
cols = 31
partition_thickness = 1
border_thickness = 13
width = 800
height = 600
partition_color = (255,255,255)

#Inicia a biblioteca do pygame
pygame.init()
pygame.display.init()
pygame.font.init()

#tamanho do bloco
square_thickness = 24
window = pygame.display.set_mode((width, height))
#imagem inicial
icon = pygame.image.load('assets/icon.png')
#titulo da janela
pygame.display.set_caption("As Cobrinhas de Aélio")
pygame.display.set_icon(icon)



#função pra atualizar janela
def redrawWindow(window, borders, s1, s2, a, apple_surface):

	window.fill((255, 255, 255))
	for w in borders:
		w.draw(window)
	s1.draw(window)

	s2.draw(window)
	a.draw(window, apple_surface)
	pygame.display.update()

#função para atualizar menu
def redrawMenu(window, front_menu, wait_text, start_text):
	window.blit(front_menu, (0, 0, width, height))
	wait_text.draw(window)
	start_text.draw(window)

	pygame.display.update() 	

def client():
	main_run = True
	game_run = True 
	menu_run = True
	clock = pygame.time.Clock()
	enter_pressed = False

	apple_surface = pygame.image.load('assets/apple.png')
	front_menu = pygame.image.load('assets/front.png')

	eat_sound = pygame.mixer.Sound('assets/eat.wav')
	dead_sound = pygame.mixer.Sound('assets/dead.wav')
	winner_sound = pygame.mixer.Sound('assets/win.wav')
	music = pygame.mixer.music.load('assets/music.mp3')
	pygame.mixer.music.set_volume(0.4)
	

	wait_text = Text("Esperando oponente..", (0,128,0) , 35, 400)
	wait_text.display = False
	start_text = Text("Aperte Enter para Conectar" , (0, 0, 0) , 35, 400)
	#loop principal do jogo
	while main_run:
		pygame.mixer.music.play(-1)

		while menu_run:

			clock.tick(60)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					menu_run = False
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN :
					if event.key == pygame.K_RETURN:
						try:
							if not enter_pressed:
								print("Conectando...")
								c = Connection()
								info = c.connect()
								client_id = int(info['id'])
								print(client_id)
								game = info['game']
								enter_pressed = True
								wait_text.display = True
								start_text.display = False
					

						except Exception as e:
							print(e)
							pygame.quit()
							sys.exit()

			if enter_pressed:
				game = c.send('fetch')

				if game.ready: 	
					menu_run = False
					game_run = True
					s1 = game.snakes[client_id]
					s2 = game.snakes[1 - client_id]
					a = game.a
					G = game.g
					enter_pressed = False
					start_text.display = True
					wait_text.display = False
					break							

			redrawMenu(window, front_menu, wait_text, start_text)



		# Definindo as bordas nos cantos da tela pra representar a parede final
		borders = [Border(0, 0, width, border_thickness, (0, 0, 0)),
				   Border(0, 0, border_thickness, height, (0, 0, 0)),
				   Border(0, height - border_thickness, width, border_thickness, (0, 0, 0)),
				   Border(width - border_thickness, 0, border_thickness, height, (0, 0, 0))]

		start_x = border_thickness
		start_y = border_thickness

		while start_x < width - border_thickness-square_thickness:
			start_x += square_thickness

			# definindo bordas na vertical
			vw = Border(start_x, border_thickness, partition_thickness, height - (2 * border_thickness), partition_color)
			borders.append(vw)

			start_x += partition_thickness
			

		while start_y < height - border_thickness-square_thickness:
			start_y += square_thickness

			# definindo as bordas na horizontal
			hw = Border(border_thickness, start_y, width - (2 * border_thickness), partition_thickness, partition_color)
			borders.append(hw)

			start_y += partition_thickness

		# Informando a cor do jogador
		color_info = Text("Sua cor é: ", s1.color, 35, height/2 -100)
		
		# definindo mensagem de começo de jogo e as mudanças de cor
		for i in range(3, 0,-1): 
			window.fill((255, 255, 255))
			if i ==3:
				timer_info = Text("Jogo iniciando em... "+str(i) , (0,128,0), 35, height/2 + 100 )
			elif i == 2:
				timer_info = Text("Jogo iniciando em... "+str(i) , (255,140,0), 35, height/2 + 100 )
			else:
				timer_info = Text("Jogo iniciando em... "+str(i) , (255,0,0), 35, height/2 + 100 )
			pygame.draw.rect(window, s1.color, (round(color_info.x + color_info.width / 2 - 100 / 2), round(color_info.y + color_info.height), 100, 100))
			pygame.draw.rect(window, (255, 255, 255), (round(color_info.x + color_info.width / 2 - 100 / 2) + 25, round(color_info.y + color_info.height) + 20, 10, 10))
			pygame.draw.rect(window, (255, 255, 255), (round(color_info.x + color_info.width / 2 - 100 / 2) + 65, round(color_info.y + color_info.height) + 20, 10, 10))
			color_info.draw(window)
			timer_info.draw(window)

			pygame.display.update()
			sleep(1)


		while game_run:
			# velocidade da cobrinha
			clock.tick(10)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					game_run = False
					pygame.quit()
					sys.exit()

			collision_status = s1.verify_collision(a, eat_sound, s2)
			s1.movement()


			try:
				game.snakes[client_id] = s1
			except :
				pass

			if collision_status:
				
				game = c.send({'snake' : s1 , 'apple' : a , 'apple_collision_status' : True, 'snake_died' : False})


			else:
				game = c.send({'snake' : s1, 'apple_collision_status' : False , 'snake_died' : False})
				try:
					a = game.a
				except :
					pass

			try:		
				s2 = game.snakes[1 - client_id]	
			except :
				pass	


			redrawWindow(window, borders, s1, s2, a, apple_surface)

			if s1.dead:
				pygame.mixer.music.fadeout(500)
				# Perdeu
				dead_sound.play()
				print("Você perdeu!")
				game = c.send('killgame')
				e = GameOver(False,"Você perdeu!" , s1, s2)
				e.wait_key(window)
				
				game_run = False
				menu_run = True
				break

			elif s2.dead or game ==-1:
				pygame.mixer.music.fadeout(500)
				# Ganhou
				winner_sound.play()
				print('Você ganhou!')
				e = GameOver(True,"Você ganhou!!!" , s1, s2)
				e.wait_key(window)
				
				game_run = False
				menu_run = True
				break

client()
