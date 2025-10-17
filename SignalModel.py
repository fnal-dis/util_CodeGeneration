#!/usr/bin/env python3

import re
import yaml

import numpy as np

from pathlib import Path

regex_suffix_indices = re.compile(r'(.*[^\d])(\d*)$')

class Project :
    def __init__(self, yaml_path="./project.yaml"):
        project_yaml = yaml.safe_load(Path(yaml_path).read_text())
        self.validate_yaml(project_yaml)
        project_name, project = next(iter(project_yaml.items()))
        self.name = project_name
        for attr,val in project.items():
            self.__setattr__(attr, val)

        if "Transceiver" not in self.__dict__.keys():
            self.__setattr__("Transcveiver", False)

    def get_sheets(self):
        d = {}
        if "ports_sheet" in self.__dict__:
            d["Ports"] = self.ports_sheet
        if "bus_sheet" in self.__dict__:
            d["Digital Bus"] = self.bus_sheet

        return d

    def validate_yaml(self, yaml_dict):
        if len(yaml_dict.keys()) > 1:
            raise Exception("Only 1 project allowed in a YAML")

    @property
    def name_short(self):
        return self.project_name_short

    @property
    def basetype_name(self):
        return f"{self.name_short}_BaseType"

    @property
    def supertype_name(self):
        return f"{self.name_short}"

    @property
    def package_name(self):
        return f"pkg_{self.name}"

class Signal :


    def __init__(self, attrs : dict):
        # Data for Array signals
        self.is_array = False
        self.origin = 0
        self.index = 0

        self.attrs = attrs
        self.name = self.process_name("Net Name")
        self.bundle_name = self.process_name("Bundle Name")

        self.direction = self.attrs["DIR"].lower()


    def __getitem__(self, key):
        return self.attrs[key]

    def __repr__(self):
        s = "Signal<" + self.name + ">"
        if self.is_array:
            if self.origin != 0:
                s += f"({self.origin}-indexed)"
        return s


    def process_name(self, field):
        name = self[field]
        name = name.replace('(', '_').title()
        name = re.sub(r'[\W]+', '', name)
        name = re.sub(r'^([0-9])', r'x\1', name)
        if self.is_differential:
            name = name.replace("_P",  "")
        return name

    def set_array(self, index, first=0, last=99):
        self.is_array = True
        self.first = first
        self.last = last
        self.index = index

        r = regex_suffix_indices
        self.name = r.sub(r'\g<1>', self.name)

        # Ensure real index is 0 for correct codegen
        self.name += f"[{self.index - self.first}]"

    @property
    def is_singleended(self):
        return not self.attrs["Differential"]

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

class SignalBundle :
    def __init__(self, project, name):
        self.project = project
        self.name : str  = name
        self._signals : list(Signal) = []

    def __repr__(self):
        s = f"Bundle<{self.name}>:\n"
        for sig in self.signals:
            s += f"\t| {str(sig)}\n"
        return s

    @property
    def signals(self):
        return [s for s in self._signals]

    def assign_signal(self, signal):
        signal.parent_bundle = self
        signal.project = self.project
        if signal not in self._signals:
            # Skip _N complements of differnetial signals (keep only the _p)
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

    def consolidate_arrays(self):
        """Iterates through children and detects arrays of signals with increasing numerical suffixes"""

        d = {}

        # Detect numerical suffixes
        r = regex_suffix_indices
        for signal in self.signals:
            prefix, suffix = r.search(signal.name).groups()
            if suffix == '':
                continue
            suffix = int(suffix)
            if prefix in d:
                d[prefix].append((signal, suffix))
            else:
                d[prefix] = [(signal, suffix)]

        # Filter by length
        d = {k:v for k,v in d.items() if len(v) > 1}

        # Filter to only keep consecutive indices
        f_indices = lambda tuples: [t[1] for t in tuples]
        d = {k:v for k,v in d.items() if (np.diff(f_indices(v)) == 1).all()}

        # Set remaining signals array flag to True
        for prefix, info in d.items():
            first = min(index for signal, index in info)
            last = max(index for signal, index in info)
            for signal, index in info:
                signal.set_array(index=index, first=first, last=last)

class SignalSpecification :
    def __init__(self, project : Project):
        self.project = project
        self._bundles: dict[str, SignalBundle] = {}

        # TODO: Remove once DigitalBusSheetLoader is implemented
        self.digital_bus = None

    def new_bundle(self, bundle_name):
        bundle = SignalBundle(self.project, bundle_name)
        self._bundles[bundle.name] = bundle
        return bundle

    def get_bundle(self, name, make_if_missing=False):
        if name in self._bundles:
            bundle = self._bundles[name]
        elif make_if_missing:
            bundle = self.new_bundle(name)
        else:
            raise Exception("Bundle not found (use make_if_missing if wanting to create an empty new bundle)")
        return bundle

    def consolidate(self):
        for bundle in self.bundles:
            bundle.consolidate_arrays()

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
