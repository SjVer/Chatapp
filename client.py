#!/usr/bin/env python3

import socket, select, errno
import sys, time, os

#=====================
#PORT = 8761
#IP = '127.0.1.1'
HEADER_LENGTH = 64
FORMAT = 'utf-8'
#=====================

# get started
IP = input('Enter server IP: ')
PORT = int(input('Enter server port: '))

client_username = input('Enter username: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = client_username.encode(FORMAT)
username_header = f"{len(username):<{HEADER_LENGTH}}".encode(FORMAT)
client_socket.send(username_header + username)

while True:
	message = input("Enter a message: ")

	if message:
		message = message.encode(FORMAT)
		message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
		client_socket.send(message_header + message)

	try:
		while True:
			# receive messages
			username_header = client_socket.recv(HEADER_LENGTH)
			if not len(username_header):
				print('[SERVER] Server closed the connection.')
				sys.exit()

			username_lenght = int(username_lenght.decode(FORMAT).strip())
			username = client_socket.recv(username_lenght).decode(FORMAT)

			message_header = client_socket.recv(HEADER_LENGTH)
			message_length = int(message_header.decode(FORMAT).strip())
			message = client_socket.recv(message_length).decode(FORMAT)

			prin(f"{username}: {message}")

	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('Reading error', str(e))
			sys.exit()
		continue

	except Exception as e:
		print('General error', str(e))
		sys.exit()