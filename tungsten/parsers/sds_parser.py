import abc
from io import IOBase

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import \
    GhsSafetyDataSheet


class SdsParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse(self, io: IOBase) -> GhsSafetyDataSheet:
        pass
