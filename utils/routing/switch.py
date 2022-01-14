"""
Switches controller
"""
import serial
from typing import List, Optional
from utils.hardware import host


class Switcher:
    def __init__(self):
        self.port = host.serial_ports()[0]
        self.baudrate = 19200
        self.timeout = 0.1 # unit: s
        self.connected = None
        self.n_in = None
        self.n_out = None
        self.out_ports = None
        self.name = 'Switcher base class'

    def reset_device(self):
        self.send_command('<RESET>')

    def latch_keys(self):
        """
        0 means latched
        """
        self.send_command('<KEY_0>')

    def unlatch_keys(self):
        """
        1 means non-latched
        """
        self.send_command('<KEY_1>')

    def send_command(self, cmd: str):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            ser.write(bytes(cmd, 'utf-8'))
            res = ser.readline().decode('utf-8')
            ser.close()
            return res, True
        except:
            return None, False

    def get_status(self):
        """
        Status of current switches
        ---
        For 5x16 switch: status in form of <STATUS_z_5_a_b_c_d_e>
        1: keys are not latched
        a/b/c/d/e: gate channel index: 01~16
        e.g. <STATUS_1_5_01_01_01_01_02>
        """
        return self.send_command('<STATUS_?>')

    def get_all_outer_channels(self) -> Optional[List[int]]:
        """
        Return outer channel indices of each gate
        """
        status, self.connected = self.get_status()
        if self.connected:
            values_str = status.split('_')[3:]
            return list(map(int, values_str))
        else:
            return None

    def get_outer_channel(self, gate: int) -> Optional[int]:
        """
        Return outer channel index of one specific gate
        """
        if gate > self.n_in:
            raise ValueError('value "gate" is larger than {}'.format(self.n_in))
        status, self.connected = self.get_status()
        if self.connected:
            return status.split('_')[3:][gate - 1]
        else:
            return None

    def set_all_outer_channels(self, channel: int) -> bool:
        if self.n_out < 10:
            cmd = '<OUT{}>'.format(channel)
        else:
            cmd = '<OUT{}>'.format(str(channel).zfill(2))
        _, self.connected = self.send_command(cmd)
        return self.connected

    def set_outer_channel(self, gate: int, channel: int) -> bool:
        """
        :param gate: gate index of the input terminal
        :param channel: channel index of the output terminal
        """
        if self.n_out < 10:
            cmd = '<{}OUT{}>'.format(gate, channel)
        else:
            cmd = '<{}OUT{}>'.format(gate, str(channel).zfill(2))
        _, self.connected = self.send_command(cmd)
        return self.connected

    @property
    def status(self):
        status, self.connected = self.get_status()
        if self.connected:
            return status
        else:
            return None


class SPDSwitcher(Switcher):
    """
    SPDs Switcher: 8x8 switch
    """

    def __init__(self):
        super(SPDSwitcher, self).__init__()
        self.n_inner = 8
        self.n_outer = 8
        self.out_ports = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.name = '8x8 SPDs Switcher'


class EPSwitcher(Switcher):
    """
    EPs Switcher: 5x16 switch
    """

    def __init__(self):
        super(EPSwitcher, self).__init__()
        self.n_inner = 5
        self.n_outer = 16
        self.out_ports = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
                          '16']
        self.name = '5x16 EPs Switcher'
