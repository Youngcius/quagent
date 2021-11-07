"""
Utils functions for serial communication
"""

import serial
import sys
import glob


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
    port_status = True
    try:
        s = serial.Serial(port)
        s.close()
    except OSError:
        port_status = False
    return port_status
