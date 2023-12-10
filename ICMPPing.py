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
ICMP_TYPE_OVERTIME = 11
ICMP_ECHO_HOST_UNREACHABLE = 1
ICMP_ECHO_NETWORK_UNREACHABLE = 0
ICMP_ECHO_PROTOCOL_UNREACHABLE = 2
ICMP_TYPE_UNREACHABLE = 3

def calculate__checksum(strings):
    csum = 0
    _countto = (len(strings) / 2) * 2
    count = 0
    while count < _countto:
        _thisval = strings[count + 1] * 256 + strings[count]
        csum = csum + _thisval
        csum = csum & 0xffffffff
        count = count + 2
    if _countto < len(strings):
        csum = csum + strings[len(strings) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def parsemessage(_endreceivetime,_recedata,ID):
    byte_in_double = struct.calcsize("!d")
    senttime = struct.unpack("!d", _recedata[28: 28 + byte_in_double])[0]
    delay = (_endreceivetime - senttime) *1000
    # 4. Unpack the packet header for useful information, including the ID
    rec_header = _recedata[20:28]
    _replytype, _replycode, _replyckecksum, _replyid, _replysequence = struct.unpack('!bbHHh', rec_header)
    # 5. Check that the ID matches between the request and reply
    if _replyid == ID and _replytype == ICMP_ECHO_REPLY:
        # 6. Return total network delay
        return delay , ""
    elif _replytype == ICMP_TYPE_OVERTIME:
        return 0, "TTl overtime"  # ttl overtime/timeout
    elif _replytype == ICMP_TYPE_UNREACHABLE and _replycode == ICMP_ECHO_NETWORK_UNREACHABLE:
        return 0, "NETWORK_UNREACHABLE"  # unreachable
    elif _replytype == ICMP_TYPE_UNREACHABLE and _replycode == ICMP_ECHO_HOST_UNREACHABLE:
        return 0, "HOST_UNREACHABLE"
    elif _replytype == ICMP_TYPE_UNREACHABLE and _replycode == ICMP_ECHO_PROTOCOL_UNREACHABLE:
        return 0, "PROTOCOL_UNREACHABLE"
    else:
        return 0,  "time out"



def receiveping(_icmpsocket, ID, timeout):
    _whatready = select.select([_icmpsocket], [], [], timeout)
    _icmpsocket.settimeout(5)
    _endreceivetime = time.time()
    try:
        _recedata, addr = _icmpsocket.recvfrom(1024)
    except socket.error as e:
        delay = 0
        errortype = "request time out and packetloss"
    else:
        if _whatready[0] == []:
            delay = 0
        else:
            delay, errortype = parsemessage(_endreceivetime,_recedata,ID)
    return delay,errortype

def create_icmp_packet(ID, seq):
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, 0, ID, seq)
    _starttime = time.time()
    data = struct.pack("!d", _starttime)
    # print(_starttime)
    _checksum = calculate__checksum(header + data)
    header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, _checksum, ID, seq)
    return header + data


def ping(host, times, timeout):
    # Store result
    _sumdelay = 0.0
    _maxdelay = 0.0
    _mindelay = 1000.0
    _countreply = 0
    _counttimeout = 0
    _counterror = 0
    # Resolving ip
    _desip = socket.gethostbyname(host)
    print("Ping {0} [{1}] \n".format(host, _desip))
    for seq in range(0, times):
        # Call do one ping function
        icmp = socket.getprotobyname("icmp")
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        ID = int(random.random() * 100)
        packet = create_icmp_packet(ID,seq)
        s.sendto(packet, (host, 2000))
        delay, errortype = receiveping(s, ID, timeout)
        s.close()
        if delay == 0:
            # Analyse error causes
            packetloss = "request time out and packetloss"
            time_out = "time out"
            if errortype == packetloss or time_out:
                print(errortype)
                _counttimeout += 1
            else:
                print(errortype)
                _counterror += 1
        else:
            # Analyse
            print("delay is %.3f ms" % delay)
            _countreply += 1
            _sumdelay += delay
            _maxdelay = max(_maxdelay,delay)
            _mindelay = min(_maxdelay,delay)
    if _countreply >= 1:
        print("_maxdelay is %.3f ms\n_mindelay is %.3f ms\nAverageDelay  is %.3f ms" % (_maxdelay, _mindelay, _sumdelay / _countreply))
        print("%d error occurs\n%d timeout occurs" % (_counterror, _counttimeout))


# Config para: times, timeout
host = input("Where do you want to ping?")
times = int(input("How many times? "))
timeout = float(input("Please input timeout in ms: "))
timeout = timeout / 1000
ping(host, times, timeout)