#!/usr/bin/env python3

from abc import ABC, abstractmethod
from pandas import read_excel
import re

from SignalModel import Signal, SignalBundle, SignalSpecification, Project

class BaseSheetLoader(ABC) :
    def __init__(self, target_spec : SignalSpecification, file_name : str, sheet_name : str):
        self.target_spec = target_spec
        self.file_name = file_name
        self.sheet_name = sheet_name

    @abstractmethod
    def load(self):
        pass

class PortSheetLoader(BaseSheetLoader) :
    def load(self):
        spec = read_excel(self.file_name,
                          sheet_name=self.sheet_name,
                          dtype=str)
        # TODO: Select 'ffill'able columns by name
        spec.iloc[:, 0:3] = spec.iloc[:, 0:3].ffill()
        spec = spec.fillna('')

        # Cast boolean columns to correctly assign NA to False
        boolean_columns = ["Differential", "Transceiver", "No Connect"]
        for col in boolean_columns:
            if col in spec:
                spec[col] = spec[col].astype(bool)

        target = self.target_spec
        for port in spec.to_dict(orient='records'):
            sig = Signal(port)
            if not sig["No Connect"]:
                bundle = target.get_bundle(sig.bundle_name, make_if_missing=True)
                if "Protocol" in sig.__attrs__.keys():
                    if sig["Protocol"] is not None:
                        protocol = BundleProtocol(sig["Protocol"])
                        bundle.assign_protocol(protocol)
                    bundle.assign_signal(sig)

        self.target_spec.digital_bus = None

class DigitalBusSheetLoader(BaseSheetLoader) :
    def load(self):
        # TODO: Convert to Signal types
        spec = read_excel(self.file_name,
                          sheet_name=self.sheet_name,
                          dtype=str,
                          index_col=[0,1])
        self.target_spec.digital_bus = spec

class MissingSheetException(Exception):
    pass

class ExcelSheetLoader :
    valid_sheets = {
        'Ports' : PortSheetLoader,
        'Digital Bus': DigitalBusSheetLoader
    }

    @classmethod
    def load(cls, target_spec, filename, sheet_type, sheet):
        loader_class = cls.valid_sheets[sheet_type]
        loader_class(target_spec, filename, sheet).load()

class ExcelLoader :
    def __init__(self, filename):
        self.filename = filename

    def load(self, target_spec, sheet_dict):
        for sheet_type, sheet in sheet_dict.items():
            if sheet_type not in ExcelSheetLoader.valid_sheets:
                print(f"Loader for sheet {sheet} of type {sheet_type} not found! Skipping")
            else:
                ExcelSheetLoader.load(target_spec, self.filename, sheet_type, sheet)

if __name__ == '__main__':
    print("Main is Loaders.py")
    project = Project("../project.yaml")
    spec = SignalSpecification(project)

    loader = ExcelLoader("../../spec/LBNF_Horn_PS_controls_SOM__Simplified.xlsx")
    loader.load(spec)
