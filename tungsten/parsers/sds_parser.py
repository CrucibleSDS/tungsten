import abc
from io import IOBase

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import \
    GhsSafetyDataSheet


class SdsParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_to_ghs_sds(self, io: IOBase, sds_name="default") -> GhsSafetyDataSheet:
        """Parses a PDF into a :class:`GhsSafetyDataSheet`."""
        pass
