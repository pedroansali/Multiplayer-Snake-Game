import socket, pickle
from components import *

#responsavel por fazer conexão com o servidor e enviar mensagens
class Connection():
	def __init__(self):
		self.client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
		self.server =  socket.gethostbyname(socket.gethostname()) #ip do servidor
		self.port = 8001
		self.address = (self.server , self.port)

	def connect(self):
		try:
			self.client.connect(self.address)	
			recv = receive_decode(self.client, 'pickle')
			if recv == -1:
				return -1
			else:	 
				return recv 

		except Exception as e:
			print(e)

	def send(self, send_data):
		try:
			encoded_data = encode(send_data, 'pickle')
			self.client.send(encoded_data)
			recv = receive_decode(self.client, 'pickle')
			if recv == -1:
				return -1
			else:	 
				return recv 
		except Exception as e:
			print(e)


