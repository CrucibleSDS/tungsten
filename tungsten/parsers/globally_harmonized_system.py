from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


@dataclass
class GhsSafetyDataSheet:
    """An object representation of the SDS specified in GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)
    This aligns with OSHA Hazard Communication Standard per (https://www.osha.gov/hazcom)"""
    pass


@dataclass
class GhsSdsSection:
    title: GhsSdsSectionTitle
    subsections: list[GhsSdsSubsection]


@dataclass
class GhsSdsSubsection:
    title: GhsSdsSubsectionTitle


@dataclass
class GhsSdsItem:
    type: GhsSdsItemType
    data: any


class GhsSdsSectionTitle(Enum):
    IDENTIFICATION = 1  # SECTION 1: Identification of the substance/mixture and of the company/undertaking
    HAZARDS = 2  # SECTION 2: Hazards identification
    COMPOSITION_ = 3  # SECTION 3: Composition/information on ingredients
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
    S1_PRODUCT_IDENTIFIER = 11  # 1.1. Product identifier
    S1_RELEVANT_USES = 12  # 1.2. Relevant identified uses of the substance or mixture and uses advised against
    S1_SUPPLIER_DETAILS = 13  # 1.3. Details of the supplier of the safety data sheet
    S1_EMERGENCY_PHONE = 14  # 1.4. Emergency telephone number
    # SECTION 2: Hazards identification
    S2_SUBSTANCE_CLASS = 21  # 2.1. Classification of the substance or mixture
    S2_LABEL_ELEMENTS = 22  # 2.2. Label elements
    S2_OTHER_HAZARDS = 23  # 2.3. Other hazards
    # SECTION 3: Composition/information on ingredients
    S3_SUBSTANCES = 31  # 3.1. Substances
    S3_MIXTURES = 32  # 3.2. Mixtures
    # SECTION 4: First aid measures
    S4_MEASURES_DESCRIPTION = 41  # 4.1. Description of first aid measures
    S4_SYMPTOMS_AND_EFFECTS = 42  # 4.2. Most important symptoms and effects, both acute and delayed
    S4_IMMEDIATE_INDICATION = 43  # 4.3. Indication of any immediate medical attention and special treatment needed
    # SECTION 5: Firefighting measures
    S5_EXTINGUISHING_MEDIA = 51  # 5.1. Extinguishing media
    S5_SPECIAL_HAZARDS = 52  # 5.2. Special hazards arising from the substance or mixture
    S5_FIREFIGHTER_ADVICE = 53  # 5.3. Advice for firefighters
    # SECTION 6: Accidental release measure
    S6_PERSONAL_PRECAUTIONS = 61  # 6.1. Personal precautions, protective equipment and emergency procedures
    S6_ENVIRONMENTAL_PRECAUTIONS = 62  # 6.2. Environmental precautions
    S6_CONTAINMENT_CLEANUP = 63  # 6.3. Methods and material for containment and cleaning up
    S6_SECTION_REFERENCE = 64  # 6.4. Reference to other sections
    # SECTION 7: Handling and storage
    HANDLING_PRECAUTIONS = 71  # 7.1. Precautions for safe handling
    SAFE_STORAGE = 72  # 7.2. Conditions for safe storage, including any incompatibilities
    END_USE = 73  # 7.3. Specific end use(s)
    # SECTION 8: Exposure controls/personal protection
    CONTROL_PARAMETERS = 81  # 8.1. Control parameters
    EXPOSURE_CONTROLS = 82  # 8.2. Exposure controls
    # SECTION 9: Physical and chemical properties
    PHYSICAL_AND_CHEMICAL = 91  # 9.1. Information on basic physical and chemical properties
    OTHER_INFORMATION = 92  # 9.2. Other information
    # SECTION 10: Stability and reactivity
    REACTIVITY = 101  # 10.1. Reactivity
    CHEMICAL_STABILITY = 102  # 10.2. Chemical stability
    HAZARDOUS_REACTIONS = 103  # 10.3. Possibility of hazardous reactions
    CONDITIONS_TO_AVOID = 104  # 10.4. Conditions to avoid
    INCOMPATIBLE = 105  # 10.5. Incompatible materials
    DECOMPOSITION_PRODUCTS = 106  # 10.6. Hazardous decomposition products
    # SECTION 11: Toxicological information
    TOXICOLOGICAL_EFFECTS = 111  # 11.1. Information on toxicological effects
    # SECTION 12: Ecological information
    TOXICITY = 121  # 12.1. Toxicity
    PERSISTENCE_DEGRADABILITY = 122  # 12.2. Persistence and degradability
    BIOACCUMULATIVE_POTENTIAL = 123  # 12.3. Bioaccumulative potential
    MOBILITY_IN_SOIL = 124  # 12.4. Mobility in soil
    PBT_AND_VPVB = 125  # 12.5. Results of PBT and vPvB assessment
    OTHER_EFFECTS = 126  # 12.6. Other adverse effects
    # SECTION 13: Disposal considerations
    WASTE_TREATMENT = 131  # 13.1. Waste treatment methods
    # SECTION 14: Transport information
    UN_NUMBER = 141  # 14.1. UN number
    UN_SHIPPING_NAME = 142  # 14.2. UN proper shipping name
    HAZARD_CLASSES = 143  # 14.3. Transport hazard class(es)
    PACKING_GROUP = 144  # 14.4. Packing group
    ENVIRONMENTAL = 145  # 14.5. Environmental hazards
    SPECIAL_PRECAUTIONS = 146  # 14.6. Special precautions for user
    BULK_ANNEX_II_MARPOL_IBC = 147  # 14.7. Transport in bulk according to Annex II of MARPOL and the IBC Code
    # SECTION 15: Regulatory information
    REGULATIONS_LEGISLATION = 151  # 15.1. Safety, health and environmental regulations/legislation specific for the substance or mixture
    CHEMICAL_SAFETY = 152  # 15.2. Chemical safety assessment
    # SECTION 16: Other information
    DATE_OF_REVISION = 161  # 16.2. Date of the latest revision of the SDS


class GhsSdsItemType(Enum):
    TEXT = 1
    FIELD = 2
    LIST = 3
    FIGURE_HAZARD = 4
    FIGURE_OTHER = 5
