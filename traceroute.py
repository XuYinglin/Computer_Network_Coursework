#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import struct
import time
import select
import random

ICMP_TYPE_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_TYPE_ECHO_REPLY = 0  # ICMP type code for echo reply messages
ICMP_TYPE_TTL_IS_0 = 11
ICMP_TYPE_ERROR = 3
ICMP_ERROR_CODE_HOST_UNREACHABLE = 1
ICMP_ERROR_CODE_NETWORK_UNREACHABLE = 0
ICMP_ERROR_CODE_PROTOCOL_UNREACHABLE = 2
ICMP_ERROR_CODE_PORT_UNREACHABLE = 3


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


def receivePing(icmpSocket, id, seq, timeout):
    whatReady = select.select([icmpSocket], [], [],1)
    receivetime = time.time()
    if whatReady[0] == []:
        return receivetime, True, -1, 0
    receData, addr = icmpSocket.recvfrom(1024)
    # get other info
    icmpHeader = receData[20:28]
    type, code, checksum, ID, sequence = struct.unpack("BBHHH", icmpHeader)
    # if error
    # if type == ICMP_TYPE_ERROR:
    #     return -1.0, True, code,addr[0]
    # if match ID and seq
    if type == ICMP_TYPE_TTL_IS_0:
        return receivetime,False,-1,addr[0]



def create_icmp_packet(ID, seq):
    header = struct.pack("BBHHH", ICMP_TYPE_ECHO_REQUEST, 0, 0, ID, seq)
    startTime = time.time()
    data = struct.pack("d", startTime)
    # print(startTime)
    checkSum = calculate_checksum(header + data)
    header = struct.pack("BBHHH", ICMP_TYPE_ECHO_REQUEST, 0, checkSum, ID, seq)
    return header + data


def traceroute(host, max_hops ,times=4, timeout=1):
    desIp = socket.gethostbyname(host)
    icmp = socket.getprotobyname("icmp")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    s.settimeout(0.5)
    for ttl in range(1, max_hops):
        # Call do one ping function
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
        print(ttl)
        ID = int(random.random() * 100)
        packet = create_icmp_packet(ID,10)
        receivelist = ["time out","time out","time out","time out"]
        for packetnum in range(0,4):
            s.sendto(packet, (desIp, 2000))
            print(str(packetnum)+"send")
            sendTime = time.time()
            recetime, error_occurs, errorCode,sourceIP = receivePing(s, ID, 10, timeout)
            print(str(packetnum)+"rece")
            delay = (recetime - sendTime)*1000
            if packetnum < 3:
                receivelist[packetnum] = delay
            else:
                receivelist[packetnum] = sourceIP
        print("{0:8} {1:8} {2:8} {3} \n".format(receivelist[0],receivelist[1],receivelist[2],receivelist[3]))

# Config para: times, timeout
host = input("Where do you want to traceroute?")
times = int(input("How many times? "))
#timeout = int(input("Please determine timeout: "))
max_hops = int(input("Please max_hops: "))
traceroute(host,max_hops,times,10000)