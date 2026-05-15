#!/usr/bin/env python3

class ProtocolSignal:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Axis:

    template_file = "bits/axis.vhd"

    def __init__(self, tdata):
        self.tdata = tdata

class Protocol:
    has_module = False
    spec = {}
    module_outputs = []

class Prot_ADS9813(Protocol):
    spec = {
        'DCLK': ProtocolSignal(direction='in', width=1),
        'FCLK': ProtocolSignal(direction='in', width=1),
        'OUT1': ProtocolSignal(direction='in', width=1),
        'OUT2': ProtocolSignal(direction='in', width=1),
        'OUT3': ProtocolSignal(direction='in', width=1),
        'OUT4': ProtocolSignal(direction='in', width=1)
    }
    module_outputs = [
        Axis(tdata=16)
    ]


class Prot_SPI(Protocol):
    spec = {
        'EN': ProtocolSignal(direction='inout', width=1),
        'SCLK': ProtocolSignal(direction='inout', width=1),
        'CS': ProtocolSignal(direction='inout', width=1),
        'MOSI': ProtocolSignal(direction='inout', width=1),
        'MISO': ProtocolSignal(direction='inout', width=1)
    }

class Prot_I2C(Protocol):
    spec = {
        'SDA': ProtocolSignal(direction='inout', width=1),
        'SCL': ProtocolSignal(direction='inout', width=1),
    }

class Prot_SFP(Protocol):
    spec = {
        'SFP_RX': ProtocolSignal(direction='in', width=1),
        'SFP_TX': ProtocolSignal(direction='out', width=1),
        'Mod_Abs': ProtocolSignal(direction='in', width=1),
        'Rx_Los': ProtocolSignal(direction='in', width=1),
        'Tx_Dis': ProtocolSignal(direction='in', width=1),
        'Tx_Fault': ProtocolSignal(direction='out', width=1),
    }

class Prot_LMK1C110(Protocol):
    spec = {
        'Sync': ProtocolSignal(direction='out', width=1),
        'En': ProtocolSignal(direction='out', width=1),
    }
