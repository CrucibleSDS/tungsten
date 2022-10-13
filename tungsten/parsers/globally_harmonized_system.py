from __future__ import annotations

import re, enum
from collections.abc import Iterable
from enum import Enum
from dataclasses import dataclass, is_dataclass, asdict
from json import JSONEncoder


def child_string(child_iterable, heading="", indent="| ", direct_child_indent="|-") -> str:
    direct_child_flag = True

    output = heading
    if isinstance(child_iterable, Iterable):
        for child in child_iterable:
            for line in str(child).splitlines():
                if direct_child_flag:
                    direct_child_flag = False
                    output += direct_child_indent + line + "\n"
                else:
                    output += indent + line + "\n"
            direct_child_flag = True
    else:
        return str(child_iterable)
    return output


@dataclass
class GhsSafetyDataSheet:
    """An object representation of the SDS specified in GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)
    This aligns with OSHA Hazard Communication Standard per (https://www.osha.gov/hazcom)"""
    name: str
    sections: list[GhsSdsSection]

    def __str__(self):
        return child_string(self.sections, heading=f"GHS Rev. 9, 2021 SDS Document\nName: {self.name}\nContent:\n")


@dataclass
class GhsSdsSection:
    title: GhsSdsSectionTitle
    subsections: list[GhsSdsSubsection]

    def __str__(self):
        return child_string(self.subsections, heading=f"Section {self.title.name}:\nSubsections:\n")


@dataclass
class GhsSdsSubsection:
    title: GhsSdsSubsectionTitle
    items: list[GhsSdsItem]

    def __str__(self):
        return child_string(self.items, heading=f"Subsection {self.title.name}:\nItems:\n")


@dataclass
class GhsSdsItem:
    type: GhsSdsItemType
    data: any

    def __str__(self):
        return child_string(self.data, heading=f"Item Type: {self.type.name}:\nItems:\n")


class GhsSdsJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (GhsSafetyDataSheet, GhsSdsSection, GhsSdsSubsection, GhsSdsItem)):
            return asdict(o)
        if isinstance(o, (GhsSdsSectionTitle, GhsSdsSubsectionTitle, GhsSdsItemType)):
            return o.name
        elif isinstance(o, list):
            return o
        elif type(o).__name__ == "HierarchyNode":
            new_dict = {"data": o.__dict__["data"], "children": o.__dict__["children"]}
            return new_dict
        else:
            return str(o)


class GhsSdsSectionTitle(Enum):
    # SECTION 1: Identification of the substance/mixture and of the company/undertaking
    IDENTIFICATION = re.compile(r"SECTION\s1")
    # SECTION 2: Hazards identification
    HAZARDS = re.compile(r"SECTION\s2")
    # SECTION 3: Composition/information on ingredients
    COMPOSITION = re.compile(r"SECTION\s3")
    # SECTION 4: First aid measures
    FIRST_AID = re.compile(r"SECTION\s4")
    # SECTION 5: Firefighting measures
    FIRE_FIGHTING = re.compile(r"SECTION\s5")
    # SECTION 6: Accidental release measure
    ACCIDENTAL_RELEASE = re.compile(r"SECTION\s6")
    # SECTION 7: Handling and storage
    HANDLING_AND_STORAGE = re.compile(r"SECTION\s7")
    # SECTION 8: Exposure controls/personal protection
    EXPOSURE_CONTROL = re.compile(r"SECTION\s8")
    # SECTION 9: Physical and chemical properties
    PHYSICAL_AND_CHEMICAL = re.compile(r"SECTION\s9")
    # SECTION 10: Stability and reactivity
    STABILITY_AND_REACTIVITY = re.compile(r"SECTION\s10")
    # SECTION 11: Toxicological information
    TOXICOLOGICAL = re.compile(r"SECTION\s11")
    # SECTION 12: Ecological information
    ECOLOGICAL = re.compile(r"SECTION\s12")
    # SECTION 13: Disposal considerations
    DISPOSAL = re.compile(r"SECTION\s13")
    # SECTION 14: Transport information
    TRANSPORT = re.compile(r"SECTION\s14")
    # SECTION 15: Regulatory information
    REGULATORY = re.compile(r"SECTION\s15")
    # SECTION 16: Other information
    OTHER = re.compile(r"SECTION\s16")


class GhsSdsSubsectionTitle(Enum):
    # SECTION 1: Identification of the substance/mixture and of the company/undertaking
    # -Product identifier
    S1_PRODUCT_IDENTIFIER = re.compile(r"(Product\sidentifiers)", re.IGNORECASE)
    # -Relevant identified uses of the substance or mixture and uses advised against
    S1_RELEVANT_USES = re.compile(r"(Relevant\sidentified\suses)", re.IGNORECASE)
    # -Details of the supplier of the safety data sheet
    S1_SUPPLIER_DETAILS = re.compile(r"(Details\sof\sthe\ssupplier)", re.IGNORECASE)
    # -Emergency telephone number
    S1_EMERGENCY_PHONE = re.compile(r"(Emergency\stelephone)", re.IGNORECASE)

    # SECTION 2: Hazards identification
    # -Classification of the substance or mixture
    S2_SUBSTANCE_CLASS = re.compile(r"(Classification\sof\sthe\ssubstance)", re.IGNORECASE)
    # -Label elements
    S2_LABEL_ELEMENTS = re.compile(r"(GHS\sLabel\selements)", re.IGNORECASE)
    # -Other hazards
    S2_OTHER_HAZARDS = re.compile(r"(Hazards\snot\sotherwise\sclassified)", re.IGNORECASE)

    # SECTION 3: Composition/information on ingredients
    # -Substances
    S3_SUBSTANCES = re.compile(r"(Substances)", re.IGNORECASE)
    # -Mixtures
    S3_MIXTURES = re.compile(r"(Mixtures)", re.IGNORECASE)

    # SECTION 4: First aid measures
    # -Description of first aid measures
    S4_MEASURES_DESCRIPTION = re.compile(r"(Description\sof)", re.IGNORECASE)
    # -Most important symptoms and effects, both acute and delayed
    S4_SYMPTOMS_AND_EFFECTS = re.compile(r"(Most\simportant\ssymptoms)", re.IGNORECASE)
    # -Indication of any immediate medical attention and special treatment needed
    S4_IMMEDIATE_INDICATION = re.compile(r"(Indication\sof\sany\simmediate)", re.IGNORECASE)

    # SECTION 5: Firefighting measures
    # -Extinguishing media
    S5_EXTINGUISHING_MEDIA = re.compile(r"(Extinguishing\smedia)", re.IGNORECASE)
    # -Special hazards arising from the substance or mixture
    S5_SPECIAL_HAZARDS = re.compile(r"(Special\shazards)", re.IGNORECASE)
    # -Advice for firefighters
    S5_FIREFIGHTER_ADVICE = re.compile(r"(Advice\sfor\sfirefighters)", re.IGNORECASE)
    # -Further information
    S5_FURTHER_INFORMATION = re.compile(r"(Further\sinformation)", re.IGNORECASE)

    # SECTION 6: Accidental release measure
    # -Personal precautions, protective equipment and emergency procedures
    S6_PERSONAL_PRECAUTIONS = re.compile(r"(Personal\sprecautions)", re.IGNORECASE)
    # -Environmental precautions
    S6_ENVIRONMENTAL_PRECAUTIONS = re.compile(r"(Environmental\sprecautions)", re.IGNORECASE)
    # -Methods and material for containment and cleaning up
    S6_CONTAINMENT_CLEANUP = re.compile(r"(Methods\sand\smaterials)", re.IGNORECASE)
    # -Reference to other sections
    S6_SECTION_REFERENCE = re.compile(r"(Reference\sto\sother)", re.IGNORECASE)

    # SECTION 7: Handling and storage
    # -Precautions for safe handling
    S7_HANDLING_PRECAUTIONS = re.compile(r"(Precautions\sfor\ssafe\shandling)", re.IGNORECASE)
    # -Conditions for safe storage, including any incompatibilities
    S7_SAFE_STORAGE = re.compile(r"(Conditions\sfor\ssafe\sstorage)", re.IGNORECASE)
    # -Specific end use(s)
    S7_END_USE = re.compile(r"(Specific\send\suse)", re.IGNORECASE)

    # SECTION 8: Exposure controls/personal protection
    # -Control parameters
    S8_CONTROL_PARAMETERS = re.compile(r"(Control\sparameters)", re.IGNORECASE)
    # -Exposure controls
    S8_EXPOSURE_CONTROLS = re.compile(r"(Exposure\scontrols)", re.IGNORECASE)

    # SECTION 9: Physical and chemical properties
    # -Information on basic physical and chemical properties
    S9_PHYSICAL_AND_CHEMICAL = re.compile(r"(Information\son\sbasic)", re.IGNORECASE)
    # -Other information
    S9_OTHER_INFORMATION = re.compile(r"(Other\ssafety\sinformation)", re.IGNORECASE)

    # SECTION 10: Stability and reactivity
    # -Reactivity
    S10_REACTIVITY = re.compile(r"(Reactivity)", re.IGNORECASE)
    # -Chemical stability
    S10_CHEMICAL_STABILITY = re.compile(r"(Chemical\sstability)", re.IGNORECASE)
    # -Possibility of hazardous reactions
    S10_HAZARDOUS_REACTIONS = re.compile(r"(Possibility\sof\shazardous\sreactions)", re.IGNORECASE)
    # -Conditions to avoid
    S10_CONDITIONS_TO_AVOID = re.compile(r"(Conditions\sto\savoid)", re.IGNORECASE)
    # -Incompatible materials
    S10_INCOMPATIBLE = re.compile(r"(Incompatible\smaterials)", re.IGNORECASE)
    # -Hazardous decomposition products
    S10_DECOMPOSITION_PRODUCTS = re.compile(r"(Hazardous\sdecomposition)", re.IGNORECASE)

    # SECTION 11: Toxicological information
    # -Information on toxicological effects
    S11_TOXICOLOGICAL_EFFECTS = re.compile(r"(toxicological\seffects)", re.IGNORECASE)
    #    
    S11_ADDITIONAL_INFORMATION = re.compile(r"(Additional\sInformation)", re.IGNORECASE)

    # SECTION 12: Ecological information
    # -Toxicity
    S12_TOXICITY = re.compile(r"(Toxicity)", re.IGNORECASE)
    # -Persistence and degradability
    S12_PERSISTENCE_DEGRADABILITY = re.compile(r"(Persistence\sand\sdegradability)", re.IGNORECASE)
    # -Bioaccumulative potential
    S12_BIOACCUMULATIVE_POTENTIAL = re.compile(r"(Bioaccumulative)", re.IGNORECASE)
    # -Mobility in soil
    S12_MOBILITY_IN_SOIL = re.compile(r"(Mobility\sin\ssoil)", re.IGNORECASE)
    # -Results of PBT and vPvB assessment
    S12_PBT_AND_VPVB = re.compile(r"(Results\sof\sPBT)", re.IGNORECASE)
    # -Endocrine disrupting properties
    S12_ENDOCRINE_DISRUPTION = re.compile(r"(Endocrine\sdisrupting\sproperties)", re.IGNORECASE)
    # -Other effects
    S12_OTHER_EFFECTS = re.compile(r"(Other\sadverse\seffects)", re.IGNORECASE)

    # SECTION 13: Disposal considerations
    # -Waste treatment methods
    S13_WASTE_TREATMENT = re.compile(r"(Waste\streatment)", re.IGNORECASE)

    # SECTION 14: Transport information
    # -UN number
    S14_UN_NUMBER = re.compile(r"", re.IGNORECASE)
    # -UN proper shipping name
    S14_UN_SHIPPING_NAME = re.compile(r"", re.IGNORECASE)
    # -Transport hazard class(es)
    S14_HAZARD_CLASSES = re.compile(r"", re.IGNORECASE)
    # -Packing group
    S14_PACKING_GROUP = re.compile(r"", re.IGNORECASE)
    # -Environmental hazards
    S14_ENVIRONMENTAL = re.compile(r"", re.IGNORECASE)
    # -Special precautions for user
    S14_SPECIAL_PRECAUTIONS = re.compile(r"", re.IGNORECASE)
    # -Transport in bulk according to Annex II of MARPOL and the IBC Code
    S14_BULK_ANNEX_II_MARPOL_IBC = re.compile(r"", re.IGNORECASE)

    # SECTION 15: Regulatory information
    # -Safety, health and environmental regulations/legislation specific for the substance or mixture
    S15_REGULATIONS_LEGISLATION = re.compile(r"", re.IGNORECASE)
    # -Chemical safety assessment
    S15_CHEMICAL_SAFETY = re.compile(r"", re.IGNORECASE)

    # SECTION 16: Other information
    # -Other information
    S16_OTHER_INFORMATION = re.compile(r"", re.IGNORECASE)
    # -Date of the latest revision of the SDS
    S16_DATE_OF_REVISION = re.compile(r"", re.IGNORECASE)


class GhsSdsItemType(Enum):
    TEXT = enum.auto()
    FIELD = enum.auto()
    LIST = enum.auto()
    FIGURE_HAZARD = enum.auto()
    FIGURE_OTHER = enum.auto()
