#!/usr/bin/env python3

class ProtocolSignal:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Protocol:
    spec = {}

class Prot_ADS9813(Protocol):
    spec = {
        'DCLK': ProtocolSignal(direction='in', width=1),
        'FCLK': ProtocolSignal(direction='in', width=1),
        'OUT1': ProtocolSignal(direction='in', width=1),
        'OUT2': ProtocolSignal(direction='in', width=1),
        'OUT3': ProtocolSignal(direction='in', width=1),
        'OUT4': ProtocolSignal(direction='in', width=1)
    }

class Prot_SPI(Protocol):
    spec = {
        'EN': ProtocolSignal(direction='out', width=1),
        'SCLK': ProtocolSignal(direction='inout', width=1),
        'CS': ProtocolSignal(direction='inout', width=1),
        'MOSI': ProtocolSignal(direction='inout', width=1),
        'MISO': ProtocolSignal(direction='inout', width=1)
    }

class Prot_I2C(Protocol):
    spec = {
        'SDA': ProtocolSignal(direction='inout', width=1),
        'SCLK': ProtocolSignal(direction='inout', width=1),
    }

class Prot_SFP(Protocol):
    spec = {
        'Rx': ProtocolSignal(direction='inout', width=1),
        'Tx': ProtocolSignal(direction='inout', width=1),
        'Mod_Abs': ProtocolSignal(direction='in', width=1),
        'Rx_Los': ProtocolSignal(direction='in', width=1),
        'Tx_Dis': ProtocolSignal(direction='in', width=1),
        'Tx_Fault': ProtocolSignal(direction='out', width=1),
    }
