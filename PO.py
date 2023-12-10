#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import socket
import select
import sys

def send_recv_resend(_tcpsocket, _requestmes):
	# print(_requestmes)
	# Config Socket
	des = _requestmes.split("Host: ")[1].split("\r\n")[0]
	# print(des)
	des = socket.gethostbyname(des)
	# print(des)
	_toserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	_toserversocket.connect((des, 80))
	# Send request to web server
	_toserversocket.send(_requestmes.encode())
	# Receive response
	ready = select.select([_toserversocket], [], [], 2)
	if ready[0] == []:
		print("timeout")
	else:
		response = _toserversocket.recv(1024)
		# print(response)
		# Send response to client
		_tcpsocket.send(response)
	_toserversocket.close()

def handle_request(_tcpsocket):
	""" Determining the Request Type and Do Corresponding Operation"""
	# Receive request message
	_requestmes = _tcpsocket.recv(1024).decode()
	if _requestmes[0:3] == "GET":
		send_recv_resend(_tcpsocket, _requestmes)
	elif _requestmes[0:3] == "PUT":
		send_recv_resend(_tcpsocket, _requestmes)
	elif _requestmes[0:6] == "DELETE":
		send_recv_resend(_tcpsocket, _requestmes)
	else:
		# print(_requestmes[0:7])
		print("Unsupported request type")
	# Close socket
	_tcpsocket.close()


def start_web_proxy(_proxyport = 8000):
	_proxyport = int(_proxyport, 10)
	# Create TCP socket
	_proxysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind address port
	_proxysocket.bind(("127.0.0.1", _proxyport))
	# Listen for connections
	_proxysocket.listen(1)
	print("The server is ready to receive")
	while True:
		_connectionsocket, addr = _proxysocket.accept()
		handle_request(_connectionsocket)
	_proxysocket.close()

_proxyport = input("Please config port: ")
start_web_proxy(_proxyport)