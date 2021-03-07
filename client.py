#!/usr/bin/env python3

# importing n setting up n shit
if True:
	import socket, select, errno
	import sys, time, os, os_signals
	from threading import Thread
	from signal import signal, SIGWINCH
	from termcolor import colored

	#=====================
	#PORT = 8761
	#IP = '127.0.1.1'
	HEADER_LENGTH = 64
	FORMAT = 'utf-8'
	EXITCOMMAND = 'quit'
	CLOSESERVERCOMMAND = 'close-server'
	#=====================

	IP = input('Enter server IP: ')
	PORT = int(input('Enter server port: '))

	class win:
		def __init__(self):
			self.update()
		def update(self):
			self.x = os.get_terminal_size()[0]
			self.y = os.get_terminal_size()[1]
	win = win()

# get started
if True:
	client_username = input('Enter username: ')

	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((IP, PORT))
		client_socket.setblocking(False)
	except ConnectionRefusedError:
		print(colored('Could not connect to server.', 'yellow', attrs=['bold']))
		sys.exit()

	print(colored('Connected to server. Type "quit" to exit.', 'blue', attrs=['bold']))
	print(colored('-----------------------------------------', 'blue', attrs=['bold']))

	username = client_username.encode(FORMAT)
	username_header = f"{len(username):<{HEADER_LENGTH}}".encode(FORMAT)
	client_socket.send(username_header + username)

def sender():
	global win
	while True:
		message = input("")

		if message == EXITCOMMAND:
			print(colored('Closed connection. Quitting...', 'blue', attrs=['bold']))
			message = f"\b\b has left the server."
			message = message.encode(FORMAT)
			message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
			client_socket.send(message_header + message)
			os_signals.send_signal('SIGKILL')

		if message == CLOSESERVERCOMMAND:
			print(colored('Closed the server. Quitting...', 'blue', attrs=['bold']))
			message = f"\b\b has closed the server."
			message = message.encode(FORMAT)
			message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
			client_socket.send(message_header + message)
			os_signals.send_signal('SIGKILL')

		try:
			message = message.encode(FORMAT)
			message_header = f"{len(message):<{HEADER_LENGTH}}".encode(FORMAT)
			client_socket.send(message_header + message)
		except:
			pass

def receiver():
	global win
	while True:
		try:
			while True:
				# receive messages
				username_header = client_socket.recv(HEADER_LENGTH)
				if not len(username_header):
					print(colored('[SERVER] Server closed the connection.', 'yellow', attrs=['bold']))
					os_signals.send_signal('SIGKILL')

				username_length = int(username_header.decode(FORMAT).strip())
				username = client_socket.recv(username_length).decode(FORMAT)

				message_header = client_socket.recv(HEADER_LENGTH)
				message_length = int(message_header.decode(FORMAT).strip())
				message = client_socket.recv(message_length).decode(FORMAT)

				print(colored(f"{username}: {message}", 'green', attrs=['bold']))

				if message == ' has closed the server.':
					print(colored('Server closed. Quitting...', 'blue', attrs=['bold']))
					os_signals.send_signal('SIGKILL')

		except IOError as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print(colored('Reading error', str(e), 'red', attrs=['bold']))
				os_signals.send_signal('SIGKILL')
			continue

		except Exception as e:
			print(colored('General error', str(e), 'red', attrs=['bold']))
			os_signals.send_signal('SIGKILL')

def resize_handler(signum, frame):
	global win
	win.update()

signal(SIGWINCH, resize_handler)
Thread(target=receiver).start()
Thread(target=sender).start()