#!/usr/bin/env python3

# startup
if True:
	import socket, sys, time, os, threading, select

	#=====================
	PORT = 8761
	IP = socket.gethostbyname(socket.gethostname())
	# 127.0.1.1
	HOST = socket.gethostname()
	HEADER_LENGTH = 64
	FORMAT = 'utf-8'
	EXITCOMMAND = 'quit'
	#=====================

	# server startup
	print('[SERVER] server startup...')
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((IP, PORT))
		print(f"[SERVER] Server bound. IP: {IP} port: {PORT}")
	except OSError:
		print(f"[SERVER] Could not bind. Aborting...\n")
		server.close()
		os.system('pkill -f ".py"')

	server.listen()
	print(f"[SERVER] Listening for connections...")
	sockets_list = [server]
	sockets_write_list = []
	clients = {}

def receive_message(client_socket):
    try:
        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode(FORMAT).strip())

        # Return an object of message header and message data
        return {'header': message_header, 'content': client_socket.recv(message_length)}

    except:
        return False

while True:
	read_sockets, write_sockets, exception_sockets = select.select(sockets_list, sockets_write_list, sockets_list)

	for notified_socket in read_sockets:
		if notified_socket == server:
			# someone connected
			client_socket, client_address = server.accept()
			user = receive_message(client_socket)
			if user is False:
				# someone disconnected
				continue

			sockets_list.append(client_socket)
			clients[client_socket] = user

			info1 = f"{client_address[0]}:{client_address[1]}"
			info2 = f"{user['content'].decode(FORMAT)}"
			print(f'[SERVER] New connection from {info1} username: {info2}')

		else:
			# received message
			message = receive_message(notified_socket)

			if message is False:
				# client closed connection
				print(f"[SERVER] Closed connection from {clients[notified_socket]['content'].decode(FORMAT)}")
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			user = clients[notified_socket]
			print(f"[SERVER] Received message from {user['content'].decode(FORMAT)}: '{message['content'].decode(FORMAT)}'")

			# spread message
			for client_socket in clients:
				if client_socket != notified_socket:
					client_socket.send(user['header'] + user['content'] + message['header'] + message['content'])

	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]
	