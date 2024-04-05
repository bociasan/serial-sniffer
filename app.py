import sys
import threading

import serial.tools.list_ports
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QPushButton, QGroupBox, QLabel,
                             QListView, QMessageBox, QLineEdit)

MAX_SERIALS = 4
MAX_ROWS = 50


def get_available_ports():
    com_ports = []
    ports = serial.tools.list_ports.comports()
    sorted_com_ports = sorted(ports, key=lambda x: int(x[0][3:]))
    for port in sorted_com_ports:
        port_name = port.device
        port_description = port.description
        com_ports.append(f"{port_name} - {port_description}")
    return com_ports


def uart_listen(finish_func, idx, ser, log):
    try:
        while True:
            bs = ser.read(256)
            if len(bs):
                bs_list = list(bs)
                my_hex = ' '.join(f'{i:02X}' for i in bs_list)
                log(idx, f'[{len(bs_list)}] : {my_hex} \n')
    except Exception as e:
        print(e)
    finish_func(idx)


class SerialSniffer(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        # self.layout.setAlignment(Qt.AlignTop)

        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop)
        self.left_groupbox = QGroupBox()
        self.right_groupbox = QGroupBox()
        self.right_groupbox.setFixedWidth(250)
        self.left_groupbox.setLayout(self.left_layout)
        self.right_groupbox.setLayout(self.right_layout)

        self.serial_settings = []
        self.serial_data_list = []
        self.serial_data = []
        self.serial_stream = []
        self.serial_models = []
        self.serial_combos = []
        self.buttons_visibility = []
        self.data_inputs = []
        self.encodings = []
        # self.current_num_serials = 0
        self.dropdown = QComboBox()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SerialSniffer')
        self.setGeometry(100, 100, 400, 200)

        self.main_layout.addWidget(self.left_groupbox)
        self.main_layout.addWidget(self.right_groupbox)

        settings_groupbox = QGroupBox(f'Settings')
        settings_groupbox_layout = QVBoxLayout()
        settings_groupbox.setLayout(settings_groupbox_layout)
        dropdown_label = QLabel("Count:")

        settings_row1_layout = QHBoxLayout()
        settings_row1_layout.addWidget(dropdown_label)
        settings_row1_layout.addWidget(self.dropdown)
        settings_groupbox_layout.addLayout(settings_row1_layout)

        settings_row2_layout = QHBoxLayout()
        com_refresh_button = QPushButton("Refresh")
        com_refresh_button.clicked.connect(self.update_all_dropdown_ports)
        settings_row2_layout.addWidget(com_refresh_button)
        settings_groupbox_layout.addLayout(settings_row2_layout)

        self.right_layout.addWidget(settings_groupbox)
        self.dropdown.addItems([str(i) for i in range(MAX_SERIALS + 1)])  # Dropdown starts from 1
        self.dropdown.currentIndexChanged.connect(self.set_serials)
        self.dropdown.setCurrentIndex(2)
        # self.set_serials()

    def set_serials(self):
        num_serials = int(self.dropdown.currentText())
        current_num_serials = len(self.serial_settings)
        if num_serials > current_num_serials:
            for i in range(current_num_serials, num_serials):
                ### SETTINGS ### noqa
                serial_groupbox = QGroupBox(f'Serial {i+1}')
                serial_groupbox.setFixedHeight(180)
                serial_groupbox_layout = QVBoxLayout()
                buttons_layout = QHBoxLayout()

                comport_layout = QHBoxLayout()
                comport_dropdown = QComboBox()
                comport_dropdown.clear()
                comport_dropdown.addItems(get_available_ports())
                comport_label = QLabel("Select COM:")
                comport_label.setAlignment(Qt.AlignRight)
                comport_layout.addWidget(comport_label)
                comport_layout.addWidget(comport_dropdown)
                serial_groupbox_layout.addLayout(comport_layout)

                comspeed_layout = QHBoxLayout()
                comspeed_dropdown = QComboBox()
                COM_SPEEDS = ["110", "300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200",
                              "230400", "460800", "921600"]
                comspeed_dropdown.addItems(COM_SPEEDS)
                comspeed_dropdown.setCurrentIndex(9)
                comspeed_label = QLabel("SPEED:")
                comspeed_label.setAlignment(Qt.AlignRight)
                comspeed_layout.addWidget(comspeed_label)
                comspeed_layout.addWidget(comspeed_dropdown)
                serial_groupbox_layout.addLayout(comspeed_layout)

                encodings_layout = QHBoxLayout()
                items = ["ASCII", "BINARY"]
                rx_encoding_dropdown = QComboBox()
                tx_encoding_dropdown = QComboBox()
                rx_encoding_dropdown.addItems(items)
                tx_encoding_dropdown.addItems(items)
                rx_encoding_dropdown.setCurrentIndex(1)
                tx_encoding_dropdown.setCurrentIndex(1)
                encodings_layout.addWidget(rx_encoding_dropdown)
                encodings_layout.addWidget(tx_encoding_dropdown)
                serial_groupbox_layout.addLayout(encodings_layout)

                serial_groupbox_layout.addLayout(comport_layout)
                serial_groupbox.setLayout(serial_groupbox_layout)
                serial_groupbox_layout.addLayout(comport_layout)
                serial_groupbox_layout.addLayout(buttons_layout)
                test_com_button = QPushButton("Test COM")
                clear_button = QPushButton("Clear")
                serial_groupbox_layout.addWidget(test_com_button)
                serial_groupbox_layout.addWidget(clear_button)
                test_com_button.clicked.connect(lambda _, idx=i: self.test_com_onclick(idx))
                clear_button.clicked.connect(lambda _, idx=i: self.clear_data_onclick(idx))

                open_button = QPushButton('Open')
                close_button = QPushButton('Close')
                print("Value of crt:", i)
                open_button.clicked.connect(lambda _, idx=i: self.start_listening(idx))
                close_button.clicked.connect(lambda _, idx=i: self.serial_close(idx))
                buttons_layout.addWidget(open_button)
                buttons_layout.addWidget(close_button)

                self.serial_combos.append([comport_dropdown, comspeed_dropdown])
                self.serial_settings.append(serial_groupbox)
                self.right_layout.addWidget(serial_groupbox)

                ### DATA ### noqa
                data_groupbox = QGroupBox(f'Serial {i+1}')
                data_groupbox.setMinimumWidth(500)
                data_groupbox.setMinimumHeight(200)
                data_groupbox_layout = QVBoxLayout()
                data_groupbox.setLayout(data_groupbox_layout)
                model = QStringListModel()
                data_list = QListView()
                data_list.setModel(model)
                data_groupbox_layout.addWidget(data_list)

                send_layout = QHBoxLayout()
                input_field = QLineEdit()
                input_field.setEnabled(False)
                send_layout.addWidget(input_field)
                send_button = QPushButton("Send")
                send_button.setEnabled(False)
                send_button.clicked.connect(lambda _, idx=i: self.serial_send(idx))
                send_layout.addWidget(send_button)

                data_groupbox_layout.addLayout(send_layout)
                self.serial_data_list.append(data_list)
                self.serial_data.append(data_groupbox)
                self.serial_stream.append(None)
                self.serial_models.append(model)
                self.data_inputs.append(input_field)
                self.left_layout.addWidget(data_groupbox)

                self.buttons_visibility.append([open_button.setEnabled,
                                                close_button.setEnabled,
                                                test_com_button.setEnabled,
                                                input_field.setEnabled,
                                                send_button.setEnabled,
                                                comport_dropdown.setEnabled,
                                                comspeed_dropdown.setEnabled
                                                ])

        elif num_serials < current_num_serials:
            for i in range(num_serials, current_num_serials):
                self.serial_close(i)

                ### SETTINGS ### noqa
                self.serial_combos.pop()
                self.serial_close(len(self.serial_stream))
                self.serial_stream.pop()
                self.buttons_visibility.pop()
                item = self.serial_settings.pop()
                item.deleteLater()

                ### DATA ### noqa

                self.serial_models.pop()
                self.serial_data_list.pop()
                self.data_inputs.pop()

                item = self.serial_data.pop()
                item.deleteLater()

    def clear_data_onclick(self, idx):
        self.serial_models[idx].setStringList([])

    def test_com_onclick(self, idx):
        selected_port = self.get_port(idx)

        if selected_port:
            try:
                self.serial_close(idx)
                self.serial_open(idx)
                _serial = self.serial_stream[idx]
                _serial.write(b"\xFF")
                _serial.close()
                # print(f"Sending \"FF\" to {selected_port}.")
            except serial.SerialException as e:
                print(f"Error: {e}")

    def update_all_dropdown_ports(self):
        for i in range(len(self.serial_combos)):
            if self.serial_combos[i][0].isEnabled():
                self.update_dropdown_ports(i)

    def update_dropdown_ports(self, idx):
        comport_dropdown = self.serial_combos[idx][0]
        comport_dropdown.clear()
        comport_dropdown.addItems(get_available_ports())

    def update_serial_model(self, idx, data):
        final = self.serial_models[idx].stringList()
        if len(final) > MAX_ROWS:
            final.pop(0)
        final.append(data)
        self.serial_models[idx].setStringList(final)
        self.serial_data_list[idx].verticalScrollBar().setValue(self.serial_data_list[idx]
                                                                .verticalScrollBar().maximum())

    def set_visibility(self, idx, op_type):
        serial_opened_states = [False, True, False, True, True, False, False]
        serial_closed_states = [True, False, True, False, False, True, True]

        states = serial_opened_states if op_type else serial_closed_states

        try:
            setter = self.buttons_visibility[idx]
            for i, value in enumerate(states):
                setter[i](value)
        except Exception: # noqa
            pass

    def start_listening(self, idx):
        self.serial_open(idx)
        self.set_visibility(idx, True)
        threading.Thread(target=uart_listen,
                         args=(self.thread_finished, idx, self.serial_stream[idx], self.update_serial_model)).start()

    def serial_send(self, idx):
        # msg = b"Hello!"
        text = self.data_inputs[idx].text().upper()
        # msg = text.encode()
        try:
            msg = bytes.fromhex(text)
        except Exception as e:
            QMessageBox.information(self, "Alert", str(e))
            return

        try:
            self.serial_stream[idx].write(msg)
        except Exception as e:
            print(e)

    def get_port(self, idx):
        return self.serial_combos[idx][0].currentText().split(" ")[0]

    def get_speed(self, idx):
        return self.serial_combos[idx][1].currentText().split(" ")[0]

    def serial_open(self, idx):
        selected_port = self.get_port(idx)
        selected_speed = self.get_speed(idx)
        try:
            self.serial_stream[idx] = serial.Serial(selected_port, selected_speed, timeout=0.1)
        except Exception as e:
            QMessageBox.information(self, "Alert", str(e))

    def serial_close(self, idx):
        self.set_visibility(idx, False)
        try:
            self.serial_stream[idx].close()
        except Exception as e: # noqa
            pass
            # QMessageBox.information(self, "Alert", str(e))

    def thread_finished(self, idx):
        # print("Thread has finished")
        # self.enable_buttons(idx)
        self.serial_close(idx)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SerialSniffer()
    window.show()
    sys.exit(app.exec_())
