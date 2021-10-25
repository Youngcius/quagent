import serial
import sys


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM{}'.format(i + 1) for i in range(10)]
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


print(serial_ports())
