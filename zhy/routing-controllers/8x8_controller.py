import sys

import serial

from PyQt5.QtGui import *

from PyQt5 import QtCore

from PyQt5.QtWidgets import (QLineEdit, QWidget, QGroupBox, QCheckBox, QGridLayout, QPushButton, QApplication,
                             QHBoxLayout, QLabel, QComboBox, QStyleFactory, QSizePolicy)


# Create a class for the GUI

class basicWindow(QWidget):

    def __init__(self):

        super().__init__()

        # Create the main window for the GUI and define the default serial port in Windows

        # Serial port may change depending on which usb slot the serial connector is inserted

        self.MainGroupBox = QGroupBox()

        self.port = 'COM3'

        self.read_connection = QLabel("this is wrong")

        # Create a checkbox which is checked if the connection is Established

        # Set the font and prevent the checkbox from being able to be toggled by the user

        self.connected = QCheckBox("Connection Established")

        self.connected.setFont(QFont('AnyStyle', 10))

        self.connected.toggled.connect(self.prevent_toggle_disconnected)

        # Set the style of the GUI and resize so it looks decent on laptops

        QApplication.setStyle(QStyleFactory.create('Fusion'))

        QApplication.setPalette(QApplication.style().standardPalette())

        self.resize(self.size())

        # Disable checking the the connection established checkbox

        self.disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        # Gray out the drob down menus if there is no connection established

        # This makes it easier for the software to operate without encountering errors and closing

        # Comment out to test drop down menus when no switch is connected

        self.disableWidgetsCheckBox.toggled.connect(self.MainGroupBox.setDisabled)

        # Create the main box to set the switch configuration

        self.createMainGroupBox()

        # Create a label for the port entry

        port_inst = QLabel('Serial Port (Default is COM3)')

        port_inst.setFont(QFont('AnyStyle', 10))

        # Create a text box to manually type the serial port to connect to

        self.port_entry = QLineEdit()

        f = self.port_entry.font()

        f.setPointSize(10)

        self.port_entry.setFont(f)

        self.port_entry.setText("COM3")

        # Create a retry button which will retry a connection to the port entered in the text box

        retry_con = QPushButton("Retry")

        retry_con.setFont(QFont('AnyStyle', 10))

        retry_con.clicked.connect(self.con_again)

        # Create the layout for the GUI

        grid_layout = QGridLayout()

        grid_layout.addWidget(self.connected, 0, 0)

        grid_layout.addWidget(port_inst, 1, 0)

        grid_layout.addWidget(self.port_entry, 1, 1)

        grid_layout.addWidget(retry_con, 1, 2)

        # ------------------------!!

        grid_layout.addWidget(self.MainGroupBox, 2, 0, 10, 3)

        self.setLayout(grid_layout)

        self.setWindowTitle('Entangled Photon Routing')

    def createMainGroupBox(self):

        # Set the style for the box with drop down menus

        Instruction = QLabel("Enter Photon Destinations")

        Instruction.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        Instruction.setFont(QFont('AnyStyle', 14))

        # Create a reset button to reset the configuration to current switch configuration

        reset_config = QPushButton("Reset")

        reset_config.setFont(QFont('AnyStyle', 10))

        reset_config.clicked.connect(self.set_dropdown)

        # Create an update button which will update the switch configuration according to the

        # current selection in the drop down boxes

        update_config = QPushButton("Update")

        update_config.setFont(QFont('AnyStyle', 10))

        update_config.clicked.connect(self.send_new_config)

        # Create strings with names for each of the ports.

        # ToDo make this dependent on external file so it can be changed without altering code

        # str_ports = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16']

        str_ports = ['1', '2', '3', '4', '5', '6', '7', '8']

        # str_ports_com1 = ['ECE SNSPD 1','CWDM 1','03','04','05','06','07','08','09','10','11','12','13','14','15','16']

        str_ports_com1 = str_ports

        str_ports_com2 = str_ports

        str_ports_com3 = str_ports

        str_ports_com4 = str_ports

        str_ports_com5 = str_ports

        str_ports_com6 = str_ports

        str_ports_com7 = str_ports

        str_ports_com8 = str_ports

        self.com1_dict = {}

        self.com2_dict = {}

        self.com3_dict = {}

        self.com4_dict = {}

        self.com5_dict = {}

        self.com6_dict = {}

        self.com7_dict = {}

        self.com8_dict = {}

        # Create lookup dictionaries for drop down labels and port numbers. Include a reverse lookup as well.

        # Reverse lookup should work since this should be a 1 to 1 mapping for each common port

        for i in range(0, 8):
            self.com1_dict[str_ports_com1[i]] = str_ports[i]

            self.com1_dict[str_ports[i]] = str_ports_com1[i]

            self.com2_dict[str_ports_com2[i]] = str_ports[i]

            self.com2_dict[str_ports[i]] = str_ports_com2[i]

            self.com3_dict[str_ports_com3[i]] = str_ports[i]

            self.com3_dict[str_ports[i]] = str_ports_com3[i]

            self.com4_dict[str_ports_com4[i]] = str_ports[i]

            self.com4_dict[str_ports[i]] = str_ports_com4[i]

            self.com5_dict[str_ports_com5[i]] = str_ports[i]

            self.com5_dict[str_ports[i]] = str_ports_com5[i]

            self.com6_dict[str_ports_com6[i]] = str_ports[i]

            self.com6_dict[str_ports[i]] = str_ports_com6[i]

            self.com7_dict[str_ports_com7[i]] = str_ports[i]

            self.com7_dict[str_ports[i]] = str_ports_com7[i]

            self.com8_dict[str_ports_com8[i]] = str_ports[i]

            self.com8_dict[str_ports[i]] = str_ports_com8[i]

        # Create the drop down menus

        self.cp1_ports = QComboBox()

        self.cp1_ports.addItems(str_ports_com1)

        self.cp1_ports.setFont(QFont('AnyStyle', 10))

        self.cp2_ports = QComboBox()

        self.cp2_ports.addItems(str_ports_com2)

        self.cp2_ports.setFont(QFont('AnyStyle', 10))

        self.cp3_ports = QComboBox()

        self.cp3_ports.addItems(str_ports_com3)

        self.cp3_ports.setFont(QFont('AnyStyle', 10))

        self.cp4_ports = QComboBox()

        self.cp4_ports.addItems(str_ports_com4)

        self.cp4_ports.setFont(QFont('AnyStyle', 10))

        self.cp5_ports = QComboBox()

        self.cp5_ports.addItems(str_ports_com5)

        self.cp5_ports.setFont(QFont('AnyStyle', 10))

        self.cp6_ports = QComboBox()

        self.cp6_ports.addItems(str_ports_com6)

        self.cp6_ports.setFont(QFont('AnyStyle', 10))

        self.cp7_ports = QComboBox()

        self.cp7_ports.addItems(str_ports_com7)

        self.cp7_ports.setFont(QFont('AnyStyle', 10))

        self.cp8_ports = QComboBox()

        self.cp8_ports.addItems(str_ports_com8)

        self.cp8_ports.setFont(QFont('AnyStyle', 10))

        self.set_dropdown()

        # Create labels for the drop down menus

        cp1 = QLabel()

        cp1.setText('Placeholder 1')

        cp1.setFont(QFont('AnyStyle', 10))

        cp2 = QLabel()

        cp2.setText('Placeholder 2')

        cp2.setFont(QFont('AnyStyle', 10))

        cp3 = QLabel()

        cp3.setText('Placeholder 3')

        cp3.setFont(QFont('AnyStyle', 10))

        cp4 = QLabel()

        cp4.setText('Placeholder 4')

        cp4.setFont(QFont('AnyStyle', 10))

        cp5 = QLabel()

        cp5.setText('Placeholder 5')

        cp5.setFont(QFont('AnyStyle', 10))

        cp6 = QLabel()

        cp6.setText('Placeholder 6')

        cp6.setFont(QFont('AnyStyle', 10))

        cp7 = QLabel()

        cp7.setText('Placeholder 7')

        cp7.setFont(QFont('AnyStyle', 10))

        cp8 = QLabel()

        cp8.setText('Placeholder 8')

        cp8.setFont(QFont('AnyStyle', 10))

        # Determine where the widgets will go in the GUI

        grid_layout = QGridLayout()

        grid_layout.addWidget(Instruction, 0, 0, 1, 2)

        grid_layout.addWidget(cp1, 1, 0)

        grid_layout.addWidget(self.cp1_ports, 1, 2)

        grid_layout.addWidget(cp2, 2, 0)

        grid_layout.addWidget(self.cp2_ports, 2, 2)

        grid_layout.addWidget(cp3, 3, 0)

        grid_layout.addWidget(self.cp3_ports, 3, 2)

        grid_layout.addWidget(cp4, 4, 0)

        grid_layout.addWidget(self.cp4_ports, 4, 2)

        grid_layout.addWidget(cp5, 5, 0)

        grid_layout.addWidget(self.cp5_ports, 5, 2)

        grid_layout.addWidget(cp6, 6, 0)

        grid_layout.addWidget(self.cp6_ports, 6, 2)

        grid_layout.addWidget(cp7, 7, 0)

        grid_layout.addWidget(self.cp7_ports, 7, 2)

        grid_layout.addWidget(cp8, 8, 0)

        grid_layout.addWidget(self.cp8_ports, 8, 2)

        grid_layout.addWidget(reset_config, 9, 1)

        grid_layout.addWidget(update_config, 9, 2)

        self.MainGroupBox.setLayout(grid_layout)

    def set_dropdown(self):

        # If an conneciton is established set the drop down boxes to the current switch configuration

        output, connection = self.get_status()

        # ---------------!!

        if connection:
            self.cur_cp1 = output[12:14]

            self.cur_cp2 = output[15:17]

            self.cur_cp3 = output[18:20]

            self.cur_cp4 = output[21:23]

            self.cur_cp5 = output[24:26]

            self.cur_cp6 = output[26:28]

            self.cur_cp7 = output[28:30]

            self.cur_cp8 = output[30:32]

            connections = [self.com1_dict[self.cur_cp1], self.com2_dict[self.cur_cp2], self.com3_dict[self.cur_cp3],
                           self.com4_dict[self.cur_cp4], self.com5_dict[self.cur_cp5], self.com6_dict[self.cur_cp6],
                           self.com7_dict[self.cur_cp7], self.com8_dict[self.cur_cp8]]

            self.cp1_ports.setCurrentText(connections[0])

            self.cp2_ports.setCurrentText(connections[1])

            self.cp3_ports.setCurrentText(connections[2])

            self.cp4_ports.setCurrentText(connections[3])

            self.cp5_ports.setCurrentText(connections[4])

            self.cp6_ports.setCurrentText(connections[5])

            self.cp7_ports.setCurrentText(connections[6])

            self.cp8_ports.setCurrentText(connections[7])

    def send_command(self, command):

        # If there is a connection, send the command to the connected switch

        try:

            ser = serial.Serial(self.port, 19200, timeout=0.1)

            byte_cmd = bytes(command, 'utf-8')

            ser.write(byte_cmd)

            response = ser.readline()

            str_response = response.decode('utf-8')

            ser.close()

            return [str_response, True]

        except:

            return [None, False]

    def get_status(self):

        # Get the status and current configuration of the switch

        self.status, self.connection = self.send_command('<STATUS_?>')

        self.update_read_connection()

        self.update_connected()

        self.disableWidgetsCheckBox.setChecked(not self.connection)

        return [self.status, self.connection]

    def update_read_connection(self):

        # Determine if there is a connection

        if self.connection:

            self.read_connection.setText("Yes")

        else:

            self.read_connection.setText("No ")

        self.read_connection.setFont(QFont('AnyStyle', 10))

    def update_connected(self):

        # Update the connection established checkbox

        self.connected.toggled.disconnect()

        if self.connection:

            self.connected.toggled.connect(self.prevent_toggle_connected)

            self.connected.toggle()

        else:

            self.connected.toggled.connect(self.prevent_toggle_disconnected)

            self.connected.toggle()

    def send_new_config(self):

        # Send a new configuration to the optical switch.

        output, connection = self.get_status()

        cp1_text = str(self.cp1_ports.currentText())

        new_cp1 = self.com1_dict[cp1_text]

        cp2_text = str(self.cp2_ports.currentText())

        new_cp2 = self.com2_dict[cp2_text]

        cp3_text = str(self.cp3_ports.currentText())

        new_cp3 = self.com3_dict[cp3_text]

        cp4_text = str(self.cp4_ports.currentText())

        new_cp4 = self.com4_dict[cp4_text]

        cp5_text = str(self.cp5_ports.currentText())

        new_cp5 = self.com5_dict[cp5_text]

        cp6_text = str(self.cp6_ports.currentText())

        new_cp6 = self.com6_dict[cp6_text]

        cp7_text = str(self.cp7_ports.currentText())

        new_cp7 = self.com7_dict[cp7_text]

        cp8_text = str(self.cp8_ports.currentText())

        new_cp8 = self.com8_dict[cp8_text]

        # If the port has not changed from the previous configuration, do not send a command

        if new_cp1 != self.cur_cp1:
            self.send_command("<1OUT" + new_cp1 + ">")

        if new_cp2 != self.cur_cp2:
            self.send_command("<2OUT" + new_cp2 + ">")

        if new_cp3 != self.cur_cp3:
            self.send_command("<3OUT" + new_cp3 + ">")

        if new_cp4 != self.cur_cp4:
            self.send_command("<4OUT" + new_cp4 + ">")

        if new_cp5 != self.cur_cp5:
            self.send_command("<5OUT" + new_cp5 + ">")

        if new_cp6 != self.cur_cp6:
            self.send_command("<6OUT" + new_cp6 + ">")

        if new_cp7 != self.cur_cp7:
            self.send_command("<7OUT" + new_cp7 + ">")

        if new_cp8 != self.cur_cp8:
            self.send_command("<8OUT" + new_cp8 + ">")

        self.set_dropdown()

    def con_again(self):

        # Update the port to try connecting to

        self.port = self.port_entry.text()

        self.set_dropdown()

    def prevent_toggle_connected(self):

        # Set the toggle if connected to switch

        self.connected.setChecked(QtCore.Qt.Checked)

    def prevent_toggle_disconnected(self):

        # Untoggle if unconnected to switch

        self.connected.setChecked(QtCore.Qt.Unchecked)


# run the application

if __name__ == '__main__':
    app = QApplication(sys.argv)

    windowExample = basicWindow()

    windowExample.show()

    sys.exit(app.exec_())
