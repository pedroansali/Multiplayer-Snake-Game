import socket 
import pickle 
from _thread import * 
from components import *

#Constantes
snake_head_width = 24
snake_head_height = 24
clr_list_1 = [(0,0,128), (255,0,255), (128,0,0)]
clr_list_2 = [(128,0,128), (0,128,0), (0,255,0)]
rows = 23
cols = 31
partition_thickness = 1
border_thickness = 13
directions = ['U', 'L', 'R', 'D'] #up left right down
width = 800
height = 600
HEADERSIZE = 10

#------------------------------------------------

id_count = 0
games = {}
conn = None
server = socket.gethostbyname(socket.gethostname()) #pegar ip automaticamente do servidor
port = 8001
square_thickness = 24

S = Screen(rows, cols)

start_x = border_thickness
start_y = border_thickness

for i in range(0 , S.rows):
	for j in range(0, S.cols):
		S.screen[i][j] = Square(start_x , start_y, square_thickness,square_thickness)
		start_x += square_thickness + partition_thickness
	start_x = border_thickness
	start_y += square_thickness + partition_thickness



def threaded_client(conn , p, game_id):
	global id_count, games
	print("thread criada!")

	if p == 0 :
		color = random.choice(clr_list_1)
		games[game_id].snakes[p] = Snake(random.randint(3,rows//2), random.randint(3,cols//2), snake_head_width, snake_head_height, color, str(color), random.choice(directions), S)
	else:
		games[game_id].ready = True
		games[game_id].a = Apple(S)
		games[game_id].g = S
		color = random.choice(clr_list_2)
		games[game_id].snakes[p] = Snake(random.randint(rows//2 + 1, rows - 4), random.randint(cols//2 +1,cols - 4), snake_head_width, snake_head_height, color, str(color), random.choice(directions), S)


	initial_data =  encode({'game' : games[game_id] , 'id' :str(p)}, "pickle")

	try:
		conn.send(initial_data)
	except Exception as e:
		print(e)

	while True:
		try:
			try:
				received_data = receive_decode(conn, "pickle")
			except:
				break
				

			if game_id in games:
				game = games[game_id]

				if not received_data:
					print("Saindo da thread pois não recebeu dados!")
					break
				else:
					
					try:
						if received_data == 'fetch':

							try:
								send_data = encode(games[game_id], "pickle")
								conn.send(send_data)
							except:
								break		
						elif received_data == 'killgame':
							games[game_id].alive[p] = False 
							try:
								send_data = encode(games[game_id], "pickle")
								conn.send(send_data)
							except:
								break
														
							break	
						else:
							if received_data['apple_collision_status']:
								games[game_id].snakes[p] = received_data['snake']
								games[game_id].a = received_data['apple']
							else:
								games[game_id].snakes[p] = received_data['snake']

							if received_data['snake'].dead:
								games[game_id].alive[p] = False	

							try:	
								send_data = encode(games[game_id], "pickle")
								conn.send(send_data)
							except:
								break			

						 		

						# Send data



						if games[game_id].alive[0] == False or games[game_id] == False:
							break
					except :
						break	
			else:
				print("no game")
				break
		except Exception as e:
			print('massive exception')
			break	

	print("Conexão perdida com ", p)
	try:
		del games[game_id]
		print("Fechando o jogo", game_id)
	except:
		pass
	id_count -= 1

	conn.close()


s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
try:
	s.bind((server, port))
except:
	exit()	


s.listen(5)
print("Servidor iniciado no ip", server ,"e na porta" , port)

while True:

	try:
		conn, address = s.accept()
		print(f"Conexão {address} estabelecida")

		id_count += 1
		p = 0 

		# definindo pra qual jogo o cliente vai ser ligado
		game_id = (id_count - 1) // 2


		# Se um jogo não existe para esse cliente
		if id_count % 2 == 1:
			games[game_id] = Game(game_id)
			print("Criando novo jogo...")

		# jogo já existe pra esse cliente
		else:
			print("Juntando-se a jogo em andamento")
			p = 1		

		start_new_thread(threaded_client, (conn,p,game_id))

	except KeyboardInterrupt as e:
		if conn != None:
			conn.close()
		break  

