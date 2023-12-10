#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import socket
import select
import sys

def sendRecvResend(tcpSocket, requestMes):
	# print(requestMes)
	# Config Socket
	des = requestMes.split("Host: ")[1].split("\r\n")[0]
	# print(des)
	des = socket.gethostbyname(des)
	# print(des)
	toServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	toServerSocket.connect((des, 80))
	"""
	# Set request packet
	status = requestMes.split("\r\n")[0]
	if len(requestMes.split("\r\n\r\n")) >= 2:
		data = requestMes.split("\r\n\r\n")[1]
	else:
		data = ""
	print(status, data)
	request = status + "\r\n\r\n" + data
	"""
	# Send request to web server
	toServerSocket.send(requestMes.encode())
	# Receive response
	ready = select.select([toServerSocket], [], [], 2)
	if ready[0] == []:
		print("timeout")
	else:
		response = toServerSocket.recv(1024)
		# print(response)
		# Send response to client
		tcpSocket.send(response)
	toServerSocket.close()

def handleRequest(tcpSocket):
	""" Determining the Request Type and Do Corresponding Operation"""
	# Receive request message
	requestMes = tcpSocket.recv(1024).decode()
	if requestMes[0:3] == "GET":
		"""
		# Get url
		path = ""
		for i in requestMes[5:]:
			if i == " ":
				break
			path += i
		# If in cash
		# If not in cash
		"""
		sendRecvResend(tcpSocket, requestMes)
	elif requestMes[0:3] == "PUT":
		sendRecvResend(tcpSocket, requestMes)
	elif requestMes[0:6] == "DELETE":
		sendRecvResend(tcpSocket, requestMes)
	else:
		# print(requestMes[0:7])
		print("Unsupported request type")
	# Close socket
	tcpSocket.close()


def startWebProxy(proxyPort = 8000):
	proxyPort = int(proxyPort, 10)
	# Create TCP socket
	proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind address port
	proxySocket.bind(("10.148.111.181", proxyPort))
	# Listen for connections
	proxySocket.listen(1)
	print("The server is ready to receive")
	while True:
		connectionSocket, addr = proxySocket.accept()
		handleRequest(connectionSocket)
	proxySocket.close()

proxyPort = input("Please config port: ")
startWebProxy(proxyPort)