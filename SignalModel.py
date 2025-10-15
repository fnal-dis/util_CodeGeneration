#!/usr/bin/env python3

import re
import yaml

from pathlib import Path

class Project :
    def __init__(self, yaml_path="./project.yaml"):
        project_yaml = yaml.safe_load(Path(yaml_path).read_text())
        self.validate_yaml(project_yaml)
        project_name, project = next(iter(project_yaml.items()))
        self.name = project_name
        for attr,val in project.items():
            self.__setattr__(attr, val)

    def validate_yaml(self, yaml_dict):
        if len(yaml_dict.keys()) > 1:
            raise Exception("Only 1 project allowed in a YAML")


class Signal :

    def __init__(self, attrs : dict):
        self.attrs = attrs
        self.name = self.process_name("Net Name")
        self.bundle_name = self.process_name("Bundle Name")

    def __getitem__(self, key):
        return self.attrs[key]

    def __repr__(self):
        return "Signal<" + self.name + ">"

    def process_name(self, field):
        name = self[field]
        name = name.replace('(', '_').title()
        name = re.sub(r'[\W]+', '', name)
        name = re.sub(r'^([0-9])', r'x\1', name)
        return name

    @property
    def is_singleended(self):
        return self.attrs["Differential"] is False

    @property
    def is_differential(self):
        return not self.is_singleended and not self.attrs["Transceiver"]

    @property
    def is_transceiver(self):
        return self.attrs["Transceiver"]

    @property
    def name_io(self):
        return "io_" + self.name

    @property
    def name_signalinbundle(self):
        s = "sig_"
        s += self.project.short_name
        s += ".if_"
        s += self.bundle_name
        s += "."
        s += self.name
        s += "_"
        s += self.direction
        return s

class SignalBundle :
    def __init__(self):
        self.name : str  = None
        self.signals : list(Signal) = []

    def assign_signal(self, signal):
        signal.parent_bundle = self
        if signal not in self.signals:
            self.signals.append(signal)


class SignalSpecification :
    def __init__(self, project : Project):
        self.bundles: dict[str, SignalBundle] = {}

    @property
    def signals (self):
        for bundle in self.bundles.values():
            for sig in bundle.signals:
                yield sig

    @property
    def all_signals_singleended (self):
        return [s for s in self.signals if s.is_singleended]

    @property
    def all_signals_differential (self):
        return [s for s in self.signals if s.is_differential]

    @property
    def all_signals_transceiver (self):
        return [s for s in self.signals if s.is_transceiver]
