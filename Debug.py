#!/usr/bin/env python3

class Printer:

    def __init__(self):
        self.enabled = False

    def trace(self, cls, string, *args, **kwargs):
        if self.enabled:
            print(f"[{type(cls).__name__}]", string, *args, **kwargs)

_printer = Printer()

def enable_trace():
    _printer.enabled = True

trace = _printer.trace
