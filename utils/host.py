"""
Utils functions for serial communication, net port and other features about the Host PC
"""

import os
import serial
import sys
import glob
import socket


def serial_ports():
    """
    List available port names
    :return: a list
    """
    if sys.platform.startswith('win'):
        ports = ['COM{}'.format(i + 1) for i in range(10)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('unsupported environment')

    results = []
    for p in ports:
        try:
            s = serial.Serial(p)
            s.close()
            results.append(p)
        except serial.SerialException:
            pass
    return results


def serial_available(port):
    """
    Distinguish whether a specific port is available
    """
    port_status = True
    try:
        s = serial.Serial(port)
        s.close()
    except OSError:
        port_status = False
    return port_status


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_local_ip():
    """
    Only for Windows OS
    """
    result = []
    ipv4 = None
    ipv6 = None
    for x in os.popen('ipconfig'):
        result.append(x)
    for x in range(len(result)):
        if 'IPv4' in result[x] and result[x + 2][-2] != ' ':
            ipv4 = result[x][result[x].find(':') + 2:-1]
        elif 'IPv6' in result[x] and result[x + 3][-2] != ' ':
            ipv6 = result[x][result[x].find(':') + 2:-1]
    return ipv4, ipv6


# ipv4 = socket.gethostbyname(socket.gethostname())
ipv4 = get_host_ip()
tagger_port = 23000

print('IPv4 address:', ipv4)

if __name__ == '__main__':
    print(ipv4)
    print(get_host_ip())
    print(get_local_ip())
