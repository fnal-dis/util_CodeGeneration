#!/usr/bin/env python3
from pandas import read_excel
import re

def get_spec_data(filename, ports_sheet, project_name_short, **kwargs):

    data_ports = read_excel(filename, sheet_name=ports_sheet, dtype=str, **kwargs)
    data_ports.iloc[:,0:3] = data_ports.iloc[:,0:3].ffill()

    # Skip ports marked with "No Connect"
    data_ports = data_ports[
        ~ data_ports["No Connect"].fillna(False).astype(bool)
    ]

    # Raise error if undefined
    if data_ports[["Net Name", "Bundle Name"]].isnull().values.any():
        raise Exception("Spreadsheet has missing net/bundle name!")

    # Cast Differential column
    data_ports.Differential = data_ports.Differential.fillna(False).astype(bool)

    # Sort
    ports_in = data_ports['DIR'] == 'IN'
    data_ports[ports_in] = data_ports[ports_in].sort_values(by="Net Name")
    ports_out = data_ports['DIR'] == 'OUT'
    data_ports[ports_out] = data_ports[ports_out].sort_values(by="Net Name")

    # Removes all non-alphanumeric characters like slashes and parentheses
    # Also separates content in parentheses by an underscore
    ptn1 = re.compile(r'[\W]+')
    foo1 = lambda x: ptn1.sub('', x.replace('(', '_').title())

    # Ensures no names start with numbers, adding an "x" instead
    ptn2 = re.compile(r'^([0-9])')
    foo2 = lambda x: ptn2.sub(r'x\1', x)

    columns_to_modify = ["Net Name", "Bundle Name"]

    for col in columns_to_modify:
        data_ports[col] = data_ports[col].apply(foo1).apply(foo2)

    # Create names used for variables
    data_ports["var_io"] =          \
        "io_"                     + \
        data_ports["Net Name"]

    data_ports["var_sig"] =         \
        "sig_"                    + \
        project_name_short        + \
        ".if_"                    + \
        data_ports["Bundle Name"] + \
        "."                       + \
        data_ports["Net Name"]    + \
        "_"                       + \
        data_ports["DIR"].apply(str.lower)


    # Split single-ended vs differential ports
    differential_ports = data_ports[data_ports["Differential"] == True].copy().reset_index(drop=True)
    single_ended_ports = data_ports[data_ports["Differential"] != True].copy().reset_index(drop=True)

    # Remove differential ports' _n counterpart to simplify templates
    mask = ~differential_ports["Net Name"].str.endswith("_N")
    differential_ports = differential_ports[mask]

    # Remove _P from diff port (templates will add it back)
    mask = differential_ports["Net Name"].str.endswith("_P") * (differential_ports["Differential"] == True)
    differential_ports.loc[mask, "Net Name"] = differential_ports.loc[mask, "Net Name"].str.replace("_P", "")

    # Data struct to be passed to template engine
    data = dict(ports=data_ports,
                single_ended_ports=single_ended_ports,
                diff_ports=differential_ports)

    return data
