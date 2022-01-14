from switch import *

switch = SPDSwitcher()
print(switch.n_in, switch.n_out, switch.out_ports, switch.name)


print()
print(switch.get_status())
print(switch.status)
print(switch.get_all_outer_channels())
print()


print('set all out channels')
print(switch.set_all_outer_channels(1))
print(switch.get_status())
print()

switch.unlatch_keys()


print('set a specific outer channel')
print(switch.set_outer_channel(1, 1))
print(switch.get_all_outer_channels())
print()



print('port:', switch.port)

from utils.hardware import host

print(host.serial_ports())
print(host.serial_available('COM3'))


# print(switch.send_command('<KEY_?>'))
