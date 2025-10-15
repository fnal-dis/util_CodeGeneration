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
        spec.iloc[:, 0:3] = spec.iloc[:, 0:3].ffill() # TODO: Select 'ffill'able columns by name
        spec = spec.fillna('')

        boolean_columns = ["Differential", "Transceiver", "No Connect"]
        for col in boolean_columns:
            if col in spec:
                spec[col] = spec[col].astype(bool)

        target = self.target_spec
        for port in spec.to_dict(orient='records'):
            sig = Signal(port)
            bundle = target.get_bundle(sig.bundle_name, make_if_missing=True)
            bundle.assign_signal(sig)

class DigitalBusSheetLoader(BaseSheetLoader) :
    def load(self):
        # TODO: Convert to Signal types
        spec = read_excel(self.file_name,
                          sheet_name=self.sheet_name,
                          dtype=str,
                          index_col=[0,1])
        return spec

class ExcelSheetLoader :
    valid_sheets = {
        'Ports' : PortSheetLoader,
        'Digital Bus': DigitalBusSheetLoader
    }

    @classmethod
    def load(cls, target_spec, filename, sheet):
        if sheet not in cls.valid_sheets:
            raise Exception("Sheet " + sheet + "not found in valid_sheets")
        else:
            loader_class = cls.valid_sheets[sheet]
            loader_class(target_spec, filename, sheet).load()

class ExcelLoader :
    def __init__(self, filename):
        self.filename = filename

    def load(self, target_spec, sheet):
        ExcelSheetLoader.load(target_spec, self.filename, sheet)

if __name__ == '__main__':
    print("Main is Loaders.py")
    project = Project("../project.yaml")
    spec = SignalSpecification(project)

    loader = ExcelLoader("../../spec/LBNF_Horn_PS_controls_SOM__Simplified.xlsx")
    loader.load(spec, "Ports")
