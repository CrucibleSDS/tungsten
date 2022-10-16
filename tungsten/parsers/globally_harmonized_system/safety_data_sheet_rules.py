import abc
import re
from dataclasses import dataclass
from typing import AnyStr

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSdsSectionTitle, GhsSdsSubsectionTitle)


class GhsSdsRules(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_section_identifier(self) -> list[re.Pattern[AnyStr]]:
        pass

    @abc.abstractmethod
    def get_section_discriminator(self) -> dict[re.Pattern[AnyStr], GhsSdsSectionTitle]:
        pass

    @abc.abstractmethod
    def get_subsection_discriminator(self) -> dict[re.Pattern[AnyStr], GhsSdsSubsectionTitle]:
        pass


@dataclass
class SubsectionDiscriminator:
    matching_rules: dict[re.Pattern[AnyStr], GhsSdsSubsectionTitle]
    default: GhsSdsSubsectionTitle
