#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import struct
import time
import select
import random

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages
ICMP_ECHO_ERROR = 3
ICMP_ECHO_HOST_UNREACHABLE = 1
ICMP_ECHO_NETWORK_UNREACHABLE = 0
ICMP_ECHO_PROTOCOL_UNREACHABLE = 2
ICMP_ECHO_PORT_UNREACHABLE = 3

def calculate_checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    answer = socket.htons(answer)
    return answer


def receivePing(icmpSocket, ID, seq, timeout):
    whatReady = select.select([icmpSocket], [], [], timeout)
    Endreceive = time.time()
    if whatReady[0] == []:
        return -1.0, True, -1
    receData, addr = icmpSocket.recvfrom(1024)
    # get other info
    icmpHeader = receData[20:28]
    type, code, checksum, ID, sequence = struct.unpack("BBHHH", icmpHeader)
    # if error
    if type == ICMP_ECHO_ERROR:
        return -1.0,True,code
    # if match ID and seq
    if ID == ID and sequence == seq and code == ICMP_ECHO_REPLY:
        icmpData = receData[28:36]
        sendTime = struct.unpack("d", icmpData)
        delay = (Endreceive- sendTime[0]) * 1000
        print("From", addr[0], "reply")
        return delay,False,-1


def create_icmp_packet(ID, seq):
    header = struct.pack("BBHHH", ICMP_ECHO_REQUEST, 0, 0, ID, seq)
    startTime = time.time()
    data = struct.pack("d", startTime)
    # print(startTime)
    checkSum = calculate_checksum(header + data)
    header = struct.pack("BBHHH", ICMP_ECHO_REQUEST, 0, checkSum, ID, seq)
    return header + data


def ping(host, times, timeout):
    # Store result
    sumDelay = 0.0
    maxDelay = 0.0
    minDelay = 1000.0
    countReply = 0
    countTimeout = 0
    countError = 0
    # Resolving ip
    desIp = socket.gethostbyname(host)
    for seq in range(0, times):
        # Call do one ping function
        icmp = socket.getprotobyname("icmp")
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        ID = int(random.random() * 100)
        packet = create_icmp_packet(ID,seq)
        s.sendto(packet, (host, 2000))
        delay, error_occurs, errorCode = receivePing(s, ID, seq, timeout)
        s.close()
        if error_occurs == True:
            # Analyse error causes
            if errorCode == -1:
                print("timeout occurs")
                countTimeout += 1
            elif errorCode == ICMP_ECHO_ERRORCODE_HOST:
                print("Host Unreachable")
                countError += 1
            elif errorCode == ICMP_ECHO_ERRORCODE_PORT:
                print("Port Unreachable")
                countError += 1
            elif errorCode == ICMP_ECHO_ERRORCODE_PROTOCOL:
                print("Protocol Unreachable")
                countError += 1
            else:
                print("Unknown Error occurs")
                countError += 1
        else:
            # Analyse
            print("delay is %.3f ms" % delay)
            countReply += 1
            sumDelay += delay
            if delay > maxDelay:
                maxDelay = delay
            if delay < minDelay:
                minDelay = delay
    if countReply >= 1:
        print("MaxDelay is %.3f ms\nMinDelay is %.3f ms\nAverageDelay  is %.3f ms" % (
        maxDelay, minDelay, sumDelay / countReply))
        print("%d error occurs\n%d timeout occurs" % (countError, countTimeout))


# Config para: times, timeout
host = input("Where do you want to ping?")
times = int(input("How many times? "))
timeout = int(input("Please determine timeout: "))
ping(host, times, timeout)