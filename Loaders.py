#!/usr/bin/env python3

from abc import ABC, abstractmethod
from pandas import read_excel, read_csv
import re

from SignalModel import Signal, SignalBundle, BundleProtocol, SignalSpecification, Project

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
                if "Protocol" in sig.attrs.keys():
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
    def __init__(self, project):
        self.filename = project.spec
        self.sheet_dict = self.get_sheets(project)

    def get_sheets(self, project):
        d = {}
        if "ports_sheet" in project.__dict__:
            d["Ports"] = project.ports_sheet
        if "bus_sheet" in project.__dict__:
            d["Digital Bus"] = project.bus_sheet

        return d


    def load(self, target_spec):
        for sheet_type, sheet in self.sheet_dict.items():
            if sheet_type not in ExcelSheetLoader.valid_sheets:
                print(f"Loader for sheet {sheet} of type {sheet_type} not found! Skipping")
            else:
                ExcelSheetLoader.load(target_spec, self.filename, sheet_type, sheet)

class CsvLoader:
    def __init__(self, project):
        self.filename = project.spec

    def load(self, target_spec):
        spec = read_csv(self.filename, dtype=str, na_filter=False, index_col=False)

        #TODO: DRY wrt to PortSheetLoader
        # Cast boolean columns to correctly assign NA to False
        boolean_columns = ["Differential", "Transceiver", "No Connect"]
        for col in boolean_columns:
            if col in spec:
                spec[col] = spec[col].astype(bool)

        target = target_spec
        for port in spec.to_dict(orient='records'):
            sig = Signal(port)
            #print(f"\n\n[CsvLoader] Signal: {sig}")
            if not sig["No Connect"]:
                # THIS IS WHERE THE PROBLEM IS
                bundle = target.get_bundle(sig.bundle_name, make_if_missing=True)
                if "Protocol" in sig.attrs.keys():
                    if sig["Protocol"] is None or sig["Protocol"] == '':
                        bundle.assign_signal(sig)
                        continue

                    #print(f"[CsvLoader] Bundle: {bundle}")
                    #print(f"[CsvLoader] Bundle: {sig['Protocol']}")
                    protocol = BundleProtocol(sig["Protocol"])
                    bundle.assign_protocol(protocol)
                    bundle.assign_signal(sig)

        target_spec.digital_bus = None


class SpecLoader:

    loaders = {
        ".xlsx": ExcelLoader,
        ".csv": CsvLoader
    }

    def __init__(self, project):
        self.filename = project.spec
        self.extension = self.filename.suffix

        if self.extension not in self.loaders.keys():
            raise Exception(f"Unknown extension {self.extension}")
        else:
            self.loader = self.loaders[self.extension](project)

    def load(self, target_spec):
        self.loader.load(target_spec)


if __name__ == '__main__':
    print("Main is Loaders.py")
    project = Project("../project.yaml")
    spec = SignalSpecification(project)

    loader = ExcelLoader("../../spec/LBNF_Horn_PS_controls_SOM__Simplified.xlsx")
    loader.load(spec)
