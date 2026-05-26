#!/usr/bin/env python3

class ProtocolSignal:
    def __init__(self, name, width, direction):
        self.name = name
        self.width = width
        self.direction = direction

    def __repr__(self):
        return self.name

    @property
    def vhdl_type(self):
        if self.width == 1:
            return 'std_logic'
        elif self.width > 1:
            return f'std_logic_vector([self.width-1] downto 0)'
        else:
            return f'std_logic_vector'


class Axis:

    template_file = "bits/axis.vhd"

    def __init__(self, tdata):
        self.tdata = tdata

class Protocol:
    has_module = False
    module_outputs = []

class Prot_ADS9813(Protocol):
    signals = [
        ProtocolSignal('DCLK', direction='in', width=1),
        ProtocolSignal('FCLK', direction='in', width=1),
        ProtocolSignal('OUT1', direction='in', width=1),
        ProtocolSignal('OUT2', direction='in', width=1),
        ProtocolSignal('OUT3', direction='in', width=1),
        ProtocolSignal('OUT4', direction='in', width=1)
    ]
    module_outputs = [
        Axis(tdata=192)
    ]


class Prot_SPI(Protocol):
    signals = [
    ProtocolSignal(    'EN', direction='inout', width=1),
        ProtocolSignal('SCLK', direction='inout', width=1),
        ProtocolSignal('CS', direction='inout', width=1),
        ProtocolSignal('MOSI', direction='inout', width=1),
        ProtocolSignal('MISO', direction='inout', width=1)
    ]

class Prot_I2C(Protocol):
    signals = [
        ProtocolSignal('SDA', direction='inout', width=1),
        ProtocolSignal('SCL', direction='inout', width=1),
    ]

class Prot_SFP(Protocol):
    signals = [
        ProtocolSignal('SFP_RX', direction='in', width=1),
        ProtocolSignal('SFP_TX', direction='out', width=1),
        ProtocolSignal('Mod_Abs', direction='in', width=1),
        ProtocolSignal('Rx_Los', direction='in', width=1),
        ProtocolSignal('Tx_Dis', direction='in', width=1),
        ProtocolSignal('Tx_Fault', direction='out', width=1),
    ]

class Prot_LMK1C110(Protocol):
    signals = [
        ProtocolSignal('Sync', direction='out', width=1),
        ProtocolSignal('En', direction='out', width=1),
    ]
