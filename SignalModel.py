#!/usr/bin/env python3

import re
import yaml
import schema

from pathlib import Path

class Project :
    def __init__(self, yaml_path="./project.yaml"):
        yaml_path = Path(yaml_path)
        project_yaml = yaml.safe_load(yaml_path.read_text())
        self.validate_yaml(project_yaml)
        project_name, project = next(iter(project_yaml.items()))
        self.name = project_name
        for attr,val in project.items():
            self.__setattr__(attr, val)

        if "Transceiver" not in self.__dict__.keys():
            self.__setattr__("Transceiver", False)

        self.spec = yaml_path.parent / Path(self.spec)

    def validate_yaml(self, yaml_dict):
        if len(yaml_dict.keys()) > 1:
            raise Exception("Only 1 project allowed in a YAML")

    @property
    def name_short(self):
        return self.project_name_short

    @property
    def basetype_name(self):
        return f"t_{self.name_short}_BaseType"

    @property
    def supertype_name(self):
        return f"t_{self.name_short}"

    @property
    def package_name(self):
        return f"pkg_{self.name}"

class Signal :

    _attr_schema = schema.Schema(
        {
            "Net Name": str,
            "Bundle Name": str,
            "FPGA Pin": str,
            "IO Standard": str,
            "Direction": lambda s: s in ("in", "out", "inout"),
            "Net Name": str,
            "Differential": bool,
            "Transceiver": bool,
            "No Connect": bool,
            schema.Optional("Protocol"): str
        }
    )

    def __init__(self, attrs : dict):
        #self._attr_schema.validate(attrs)

        self.attrs = attrs
        self.name = self.process_name(self.attrs["Net Name"])
        self.bundle_name = self.process_name(self.attrs["Bundle Name"])
        self.direction = self.attrs["DIR"].lower()
        self.pin = self.attrs["FPGA Pin"]
        self.std = self.attrs["IO Standard"]

    #TODO: deprecate usage of this in the templates
    def __getitem__(self, key):
        return self.attrs[key]

    def __repr__(self):
        return "Signal<" + self.name + ">"

    def process_name(self, name_in):
        name = name_in
        name = name.replace('(', '_').title()
        name = re.sub(r'[\W]+', '', name)
        name = re.sub(r'^([0-9])', r'x\1', name)
        if self.is_differential:
            name = name.replace("_P",  "")
        return name

    @property
    def is_singleended(self):
        return not self.attrs["Differential"]

    @property
    def is_differential(self):
        return self.attrs["Differential"]

    @property
    def is_transceiver(self):
        return self.attrs["Transceiver"]

    @property
    def name_io(self):
        return f"io_{self.bundle_name}_{self.name}"

    @property
    def name_record(self):
        s = self.name
        s += "_"
        s += self.direction
        return s

    @property
    def name_signalinbundle(self):
        s = "sig_"
        s += self.project.project_name_short
        s += ".if_"
        s += self.bundle_name
        s += "."
        s += self.name
        s += "_"
        s += self.direction
        return s

class BundleProtocol:

    registered_protocols = {}
    implemented_protocols = {"SPI": [], "I2C": [], "ADS9813": []}

    def __new__(cls, name):
        if name in cls.registered_protocols:
            return cls.registered_protocols[name]
        obj = super().__new__(cls)
        cls.registered_protocols[name] = obj
        return obj

    def __init__(self, name):
        self.name : str = name

        if name not in self.implemented_protocols.keys():
            raise Warning(f"Protocol {name} has no known implementation")

    def __repr__(self):
        return f"BundleProtocol<{self.name}>"


class SignalBundle :
    def __init__(self, project, name):
        self.project = project
        self.name : str  = name
        self.protocol : BundleProtocol = None
        self._signals : list(Signal) = []

    def __repr__(self):
        s = f"Bundle<{self.name}>:\n"
        for sig in self.signals:
            s += f"\t| {str(sig)}\n"
        return s

    @property
    def signals(self):
        return [s for s in self._signals]

    def assign_protocol(self, protocol):
        if self.protocol is None:
            self.protocol = protocol
        elif protocol is not self.protocol:
            raise Exception(f"Bundle {self.name} has conflicting protocols."\
                            f" Currently has {self.protocol}, but got {protocol}.")

    def assign_signal(self, signal):
        signal.parent_bundle = self
        signal.project = self.project
        if signal not in self._signals:
            # Skip _N complements of differential signals (keep only the _p)
            if signal.is_differential and signal.name.endswith("_N"):
                return

            self._signals.append(signal)

    @property
    def record_typename(self):
        s = "t_rec_"
        s += self.project.project_name_short
        s += "_"
        s += self.name
        return s

    @property
    def interface_name(self):
        s = "if_"
        s += self.name
        return s

class SignalSpecification :
    def __init__(self, project : Project):
        self.project = project
        self._bundles: dict[str, SignalBundle] = {}

    def new_bundle(self, bundle_name):
        bundle = SignalBundle(self.project, bundle_name )
        self._bundles[bundle.name] = bundle
        return bundle

    def get_bundle(self, bundle_name, make_if_missing=False):
        if bundle_name in self._bundles:
            bundle = self._bundles[bundle_name]
        elif make_if_missing:
            bundle = self.new_bundle(bundle_name)
        else:
            raise Exception("Bundle not found (use make_if_missing if wanting to create an empty new bundle)")
        return bundle

    @property
    def signals (self):
        for bundle in self.bundles:
            for sig in bundle.signals:
                yield sig

    @property
    def bundles (self):
        return self._bundles.values()

    def signal_sort(fun):
        def wrapper(*args, **kwargs):
            out = fun(*args, **kwargs)
            out.sort(key=lambda x: x.name)
            out.sort(key=lambda x: x.direction)
            return out
        return wrapper

    @property
    @signal_sort
    def all_signals_singleended (self):
        return [s for s in self.signals if s.is_singleended]

    @property
    @signal_sort
    def all_signals_differential (self):
        return [s for s in self.signals if s.is_differential]

    @property
    @signal_sort
    def all_signals_transceiver (self):
        return [s for s in self.signals if s.is_transceiver]
