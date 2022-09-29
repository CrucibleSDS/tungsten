from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, is_dataclass, asdict
from json import JSONEncoder


@dataclass
class GhsSafetyDataSheet:
    """An object representation of the SDS specified in GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)
    This aligns with OSHA Hazard Communication Standard per (https://www.osha.gov/hazcom)"""
    name: str
    sections: list[GhsSdsSection]

    def __str__(self):
        indent = "| "
        direct_child_indent = "|-"
        direct_child_flag = True

        output = f"GHS Rev. 9, 2021 SDS Document\nName: {self.name}\nContent:\n"
        if self.sections:
            for subsection in self.sections:
                for line in str(subsection).splitlines():
                    if direct_child_flag:
                        direct_child_flag = False
                        output += direct_child_indent + line + "\n"
                    else:
                        output += indent + line + "\n"
                direct_child_flag = True
        return output


@dataclass
class GhsSdsSection:
    title: GhsSdsSectionTitle
    subsections: list[GhsSdsSubsection]

    def __str__(self):
        indent = "| "
        direct_child_indent = "|-"
        direct_child_flag = True

        output = f"Section {self.title.name}:\nSubsections:\n"
        if self.subsections:
            for subsection in self.subsections:
                for line in str(subsection).splitlines():
                    if direct_child_flag:
                        direct_child_flag = False
                        output += direct_child_indent + line + "\n"
                    else:
                        output += indent + line + "\n"
                direct_child_flag = True
        return output


@dataclass
class GhsSdsSubsection:
    title: GhsSdsSubsectionTitle
    items: list[GhsSdsItem]

    def __str__(self):
        indent = "| "
        direct_child_indent = "|-"
        direct_child_flag = True

        output = f"Subsection {self.title.name}:\nItems:\n"
        if self.items:
            for subsection in self.items:
                for line in str(subsection).splitlines():
                    if direct_child_flag:
                        direct_child_flag = False
                        output += direct_child_indent + line + "\n"
                    else:
                        output += indent + line + "\n"
                direct_child_flag = True
        return output


@dataclass
class GhsSdsItem:
    type: GhsSdsItemType
    data: any

    def __str__(self):
        indent = "| "
        direct_child_indent = "|-"
        direct_child_flag = True

        output = f"Item Type: {self.type.name}:\nItems:\n"
        if self.data:
            for line in str(self.data).splitlines():
                if direct_child_flag:
                    direct_child_flag = False
                    output += direct_child_indent + line + "\n"
                else:
                    output += indent + line + "\n"
            direct_child_flag = True
        return output


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
    IDENTIFICATION = 1  # SECTION 1: Identification of the substance/mixture and of the company/undertaking
    HAZARDS = 2  # SECTION 2: Hazards identification
    COMPOSITION = 3  # SECTION 3: Composition/information on ingredients
    FIRST_AID = 4  # SECTION 4: First aid measures
    FIRE_FIGHTING = 5  # SECTION 5: Firefighting measures
    ACCIDENTAL_RELEASE = 6  # SECTION 6: Accidental release measure
    HANDLING_AND_STORAGE = 7  # SECTION 7: Handling and storage
    EXPOSURE_CONTROL = 8  # SECTION 8: Exposure controls/personal protection
    PHYSICAL_AND_CHEMICAL = 9  # SECTION 9: Physical and chemical properties
    STABILITY_AND_REACTIVITY = 10  # SECTION 10: Stability and reactivity
    TOXICOLOGICAL = 11  # SECTION 11: Toxicological information
    ECOLOGICAL = 12  # SECTION 12: Ecological information
    DISPOSAL = 13  # SECTION 13: Disposal considerations
    TRANSPORT = 14  # SECTION 14: Transport information
    REGULATORY = 15  # SECTION 15: Regulatory information
    OTHER = 16  # SECTION 16: Other information


class GhsSdsSubsectionTitle(Enum):
    # SECTION 1: Identification of the substance/mixture and of the company/undertaking
    S1_PRODUCT_IDENTIFIER = "1.1"  # 1.1. Product identifier
    S1_RELEVANT_USES = "1.2"  # 1.2. Relevant identified uses of the substance or mixture and uses advised against
    S1_SUPPLIER_DETAILS = "1.3"  # 1.3. Details of the supplier of the safety data sheet
    S1_EMERGENCY_PHONE = "1.4"  # 1.4. Emergency telephone number
    # SECTION 2: Hazards identification
    S2_SUBSTANCE_CLASS = "2.1"  # 2.1. Classification of the substance or mixture
    S2_LABEL_ELEMENTS = "2.2"  # 2.2. Label elements
    S2_OTHER_HAZARDS = "2.3"  # 2.3. Other hazards
    # SECTION 3: Composition/information on ingredients
    S3_SUBSTANCES = "3.1"  # 3.1. Substances
    S3_MIXTURES = "3.2"  # 3.2. Mixtures
    # SECTION 4: First aid measures
    S4_MEASURES_DESCRIPTION = "4.1"  # 4.1. Description of first aid measures
    S4_SYMPTOMS_AND_EFFECTS = "4.2"  # 4.2. Most important symptoms and effects, both acute and delayed
    S4_IMMEDIATE_INDICATION = "4.3"  # 4.3. Indication of any immediate medical attention and special treatment needed
    # SECTION 5: Firefighting measures
    S5_EXTINGUISHING_MEDIA = "5.1"  # 5.1. Extinguishing media
    S5_SPECIAL_HAZARDS = "5.2"  # 5.2. Special hazards arising from the substance or mixture
    S5_FIREFIGHTER_ADVICE = "5.3"  # 5.3. Advice for firefighters
    S5_FURTHER_INFORMATION = "5.4"
    # SECTION 6: Accidental release measure
    S6_PERSONAL_PRECAUTIONS = "6.1"  # 6.1. Personal precautions, protective equipment and emergency procedures
    S6_ENVIRONMENTAL_PRECAUTIONS = "6.2"  # 6.2. Environmental precautions
    S6_CONTAINMENT_CLEANUP = "6.3"  # 6.3. Methods and material for containment and cleaning up
    S6_SECTION_REFERENCE = "6.4"  # 6.4. Reference to other sections
    # SECTION 7: Handling and storage
    S7_HANDLING_PRECAUTIONS = "7.1"  # 7.1. Precautions for safe handling
    S7_SAFE_STORAGE = "7.2"  # 7.2. Conditions for safe storage, including any incompatibilities
    S7_END_USE = "7.3"  # 7.3. Specific end use(s)
    # SECTION 8: Exposure controls/personal protection
    S8_CONTROL_PARAMETERS = "8.1"  # 8.1. Control parameters
    S8_EXPOSURE_CONTROLS = "8.2"  # 8.2. Exposure controls
    # SECTION 9: Physical and chemical properties
    S9_PHYSICAL_AND_CHEMICAL = "9.1"  # 9.1. Information on basic physical and chemical properties
    S9_OTHER_INFORMATION = "9.2"  # 9.2. Other information
    # SECTION 10: Stability and reactivity
    S10_REACTIVITY = "10.1"  # 10.1. Reactivity
    S10_CHEMICAL_STABILITY = "10.2"  # 10.2. Chemical stability
    S10_HAZARDOUS_REACTIONS = "10.3"  # 10.3. Possibility of hazardous reactions
    S10_CONDITIONS_TO_AVOID = "10.4"  # 10.4. Conditions to avoid
    S10_INCOMPATIBLE = "10.5"  # 10.5. Incompatible materials
    S10_DECOMPOSITION_PRODUCTS = "10.6"  # 10.6. Hazardous decomposition products
    # SECTION 11: Toxicological information
    S11_TOXICOLOGICAL_EFFECTS = "11.1"  # 11.1. Information on toxicological effects
    S11_ADDITIONAL_INFORMATION = "11.2"
    # SECTION 12: Ecological information
    S12_TOXICITY = "12.1"  # 12.1. Toxicity
    S12_PERSISTENCE_DEGRADABILITY = "12.2"  # 12.2. Persistence and degradability
    S12_BIOACCUMULATIVE_POTENTIAL = "12.3"  # 12.3. Bioaccumulative potential
    S12_MOBILITY_IN_SOIL = "12.4"  # 12.4. Mobility in soil
    S12_PBT_AND_VPVB = "12.5"  # 12.5. Results of PBT and vPvB assessment
    S12_ENDOCRINE_DISRUPTION = "12.6"  # 12.6. Endocrine disrupting properties
    S12_OTHER_EFFECTS = "12.7"
    # SECTION 13: Disposal considerations
    S13_WASTE_TREATMENT = "13.1"  # 13.1. Waste treatment methods
    # SECTION 14: Transport information
    S14_UN_NUMBER = "14.1"  # 14.1. UN number
    S14_UN_SHIPPING_NAME = "14.2"  # 14.2. UN proper shipping name
    S14_HAZARD_CLASSES = "14.3"  # 14.3. Transport hazard class(es)
    S14_PACKING_GROUP = "14.4"  # 14.4. Packing group
    S14_ENVIRONMENTAL = "14.5"  # 14.5. Environmental hazards
    S14_SPECIAL_PRECAUTIONS = "14.6"  # 14.6. Special precautions for user
    S14_BULK_ANNEX_II_MARPOL_IBC = "14.7"  # 14.7. Transport in bulk according to Annex II of MARPOL and the IBC Code
    # SECTION 15: Regulatory information
    S15_REGULATIONS_LEGISLATION = "15.1"  # 15.1. Safety, health and environmental regulations/legislation specific for the substance or mixture
    S15_CHEMICAL_SAFETY = "15.2"  # 15.2. Chemical safety assessment
    # SECTION 16: Other information
    S16_OTHER_INFORMATION = "16.1"
    S16_DATE_OF_REVISION = "16.2"  # 16.2. Date of the latest revision of the SDS


class GhsSdsItemType(Enum):
    TEXT = 1
    FIELD = 2
    LIST = 3
    FIGURE_HAZARD = 4
    FIGURE_OTHER = 5
