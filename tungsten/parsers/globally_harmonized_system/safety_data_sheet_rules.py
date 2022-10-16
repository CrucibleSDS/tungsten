from __future__ import annotations

import abc
import re
from dataclasses import dataclass
from typing import AnyStr

from tungsten.parsers.globally_harmonized_system.safety_data_sheet import (
    GhsSdsSectionTitle, GhsSdsSubsectionTitle)


class GhsSdsRules(metaclass=abc.ABCMeta):
    def is_section(self, text: str) -> bool:
        for pattern in self.get_section_identifier():
            if pattern.match(text) is not None:
                return True
        return False

    def discriminate_section(self, text: str) -> GhsSdsSectionTitle | None:
        for (pattern, section) in self.get_section_discriminator().items():
            if pattern.match(text) is not None:
                return section
        return None

    def is_subsection(self, text: str) -> bool:
        for pattern in self.get_subsection_identifier():
            if pattern.match(text) is not None:
                return True
        return False

    def discriminate_subsection(self, text: str, context: GhsSdsSectionTitle) -> \
            GhsSdsSubsectionTitle:
        rules = self.get_subsection_discriminator()[context]
        for (pattern, subsection) in rules.matching_rules.items():
            if pattern.search(text) is not None:
                return subsection
        return rules.default

    @abc.abstractmethod
    def get_section_identifier(self) -> list[re.Pattern[AnyStr]]:
        pass

    @abc.abstractmethod
    def get_section_discriminator(self) -> dict[re.Pattern[AnyStr], GhsSdsSectionTitle]:
        pass

    @abc.abstractmethod
    def get_subsection_identifier(self) -> list[re.Pattern[AnyStr]]:
        pass

    @abc.abstractmethod
    def get_subsection_discriminator(self) -> \
            dict[GhsSdsSectionTitle, SubsectionDiscriminatorRules]:
        pass


@dataclass
class SubsectionDiscriminatorRules:
    matching_rules: dict[re.Pattern[AnyStr], GhsSdsSubsectionTitle]
    default: GhsSdsSubsectionTitle
