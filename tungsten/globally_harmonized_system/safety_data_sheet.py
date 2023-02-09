from __future__ import annotations

import enum
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import Enum
from json import JSONEncoder
from typing import IO

from tungsten.parsers.parsing_hierarchy import HierarchyNode


@dataclass
class GhsSafetyDataSheet:
    """An object representation of the SDS specified in GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)
    This aligns with OSHA Hazard Communication Standard per (https://www.osha.gov/hazcom)
    Note that the UN GHS SDS structure is a representation of the SDS document itself, and not
    necessarily a structured representation of all fields and data."""
    name: str
    sections: list[GhsSdsSection]

    def __str__(self):
        return child_string(self.sections, heading=f"GHS Rev. 9, 2021 SDS Document\n"
                                                   f"Name: {self.name}\nContent:\n")

    def to_dict(self):
        """Convert to a dictionary."""
        return asdict(self)

    def dump(self, fp: IO[str], **kwargs: dict) -> None:
        """Serialize as a JSON formatted stream to `fp`."""
        json.dump(self.to_dict(), fp, cls=GhsSdsJsonEncoder, **kwargs)

    def dumps(self, **kwargs: dict) -> str:
        """Serialize to a JSON formatted `str`."""
        return json.dumps(self.to_dict(), cls=GhsSdsJsonEncoder, **kwargs)


class GhsSdsMetaTitle(Enum):
    VERSION = enum.auto()
    REVISION_DATE = enum.auto()
    PRINT_DATE = enum.auto()


@dataclass
class GhsSdsSection:
    """Representation of a GHS SDS section in :class:`GhsSafetyDataSheet`"""
    title: GhsSdsSectionTitle
    subsections: list[GhsSdsSubsection]

    def __str__(self):
        return child_string(self.subsections, heading=f"Section {self.title.name}:\n"
                                                      f"Subsections:\n")


@dataclass
class GhsSdsSubsection:
    """Representation of a GHS SDS subsection within a :class:`GhsSdsSection`"""
    title: GhsSdsSubsectionTitle
    items: list[GhsSdsItem]
    raw_title: str

    def __str__(self):
        return child_string(self.items, heading=f"Subsection {self.title.name}:\nItems:\n")


@dataclass
class GhsSdsItem:
    """Representation of the data contained in a GHS SDS subsection (:class:`GhsSdsSubsection`).
    This may come in the form of a field value, several field values, tables, etc.
    (This is specified in :class:`GhsSdsItemType`, though the current listing is temporary).
    Note that the UN GHS SDS structure is a representation of the SDS document itself, and not
    necessarily a structured representation of all fields and data."""
    type: GhsSdsItemType
    name: str
    data: any

    def __str__(self):
        return child_string(self.data, heading=f"Item Type: {self.type.name}:\nItems:\n")


class GhsSdsJsonEncoder(JSONEncoder):
    def default(self, o: any):
        if isinstance(o, (GhsSafetyDataSheet, GhsSdsSection, GhsSdsSubsection, GhsSdsItem)):
            return asdict(o)
        if isinstance(o, (GhsSdsSectionTitle, GhsSdsSubsectionTitle, GhsSdsItemType)):
            return o.name
        elif isinstance(o, list):
            return o
        elif isinstance(o, HierarchyNode):
            return {"data": o.data, "children": o.children}
        else:
            return str(o)


class GhsSdsSectionTitle(Enum):
    """Common enum representation of section titles specified in the UN GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)"""
    # SECTION 1: Identification of the substance or mixture and of the supplier
    IDENTIFICATION = enum.auto()
    # SECTION 2: Hazards identification
    HAZARDS = enum.auto()
    # SECTION 3: Composition/information on ingredients
    COMPOSITION = enum.auto()
    # SECTION 4: First-aid measures
    FIRST_AID = enum.auto()
    # SECTION 5: Fire-fighting measures
    FIRE_FIGHTING = enum.auto()
    # SECTION 6: Accidental release measures
    ACCIDENTAL_RELEASE = enum.auto()
    # SECTION 7: Handling and storage
    HANDLING_AND_STORAGE = enum.auto()
    # SECTION 8: Exposure controls/personal protection
    EXPOSURE_CONTROL = enum.auto()
    # SECTION 9: Physical and chemical properties
    PHYSICAL_AND_CHEMICAL = enum.auto()
    # SECTION 10: Stability and reactivity
    STABILITY_AND_REACTIVITY = enum.auto()
    # SECTION 11: Toxicological information
    TOXICOLOGICAL = enum.auto()
    # SECTION 12: Ecological information
    ECOLOGICAL = enum.auto()
    # SECTION 13: Disposal considerations
    DISPOSAL = enum.auto()
    # SECTION 14: Transport information
    TRANSPORT = enum.auto()
    # SECTION 15: Regulatory information
    REGULATORY = enum.auto()
    # SECTION 16: Other information
    OTHER = enum.auto()


class GhsSdsSubsectionTitle(Enum):
    """Common enum representation of subsection titles specified in the UN GHS Rev. 9, 2021
    (https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev9-2021)"""
    # SECTION 1: Identification of the substance or mixture and of the supplier
    # - (a) GHS Product identifier
    GHS_PRODUCT_IDENTIFIER = enum.auto()
    # - (b) Other means of identification
    OTHER_MEANS_OF_IDENTIFICATION = enum.auto()
    # - (c) Recommended use of the chemical and restrictions on use
    RECOMMENDED_USE_AND_RESTRICTIONS = enum.auto()
    # - (d) Supplier's details (including name, address, phone number etc.)
    SUPPLIER_DETAILS = enum.auto()
    # - (e) Emergency phone number
    EMERGENCY_PHONE_NUMBER = enum.auto()
    # Other information
    IDENTIFICATION_OTHER = enum.auto()

    # SECTION 2: Hazards identification
    # - (a) GHS classification of the substance/mixture and any national or regional information
    GHS_SUBSTANCE_CLASSIFICATION = enum.auto()
    # - (b) GHS label elements, including precautionary statements.
    #       (Hazard symbols may be provided as a graphical reproduction of the symbols in black and
    #       white or the name of the symbol e.g. "flame", "skull and crossbones")
    GHS_LABEL_ELEMENTS = enum.auto()
    # - (c) Other hazards which do not result in classification (e.g. "dust explosion hazard") or
    #       are not covered by the GHS.
    OTHER_HAZARDS = enum.auto()
    # Other information
    HAZARDS_OTHER = enum.auto()

    # SECTION 3: Composition/information on ingredients
    # Substance:
    # - (a) Chemical identity
    SUBSTANCE_CHEMICAL_IDENTITY = enum.auto()
    # - (b) Common name, synonyms, etc.
    SUBSTANCE_COMMON_NAME_SYNONYMS = enum.auto()
    # - (c) CAS number and other unique identifiers
    SUBSTANCE_CAS_NUMBER_IDENTIFIERS = enum.auto()
    # - (d) Impurities and stabilizing additives which are themselves classified and which
    #       contribute to the classification of the substance.
    SUBSTANCE_IMPURITIES_ADDITIVES = enum.auto()
    # Mixtures:
    # - The chemical identity and concentration or concentration ranges of all ingredients which
    #   are hazardous within the meaning of the GHS and are present above their cut-off levels.
    MIXTURE_INGREDIENTS = enum.auto()
    # Other information
    COMPOSITION_OTHER = enum.auto()

    # SECTION 4: First-aid measures
    # - (a) Description of necessary measures, subdivided according to the different routes of
    #       exposure i.e. inhalation, skin and eye contact and ingestion
    FIRST_AID_MEASURES = enum.auto()
    # - (b) Most important symptoms and effects, both acute and delayed.
    SYMPTOMS_AND_EFFECTS = enum.auto()
    # - (c) Indication of any immediate medical attention and special treatment needed, if
    #       necessary.
    INDICATION_MEDICAL_TREATMENT = enum.auto()
    # Other information
    FIRST_AID_OTHER = enum.auto()

    # SECTION 5: Fire-fighting measures
    # - (a) Suitable (and unsuitable) extinguishing media.
    EXTINGUISHING_MEDIA = enum.auto()
    # - (b) Special hazards arising from the chemical
    #       (e.g. nature of any hazardous combustion products).
    SPECIAL_HAZARDS = enum.auto()
    # - (c) Special protective equipment and precautions for fire-fighters.
    FIREFIGHTER_EQUIPMENT_PRECAUTIONS = enum.auto()
    # Other information
    FIRE_FIGHTING_OTHER = enum.auto()

    # SECTION 6: Accidental release measures
    # - (a) Personal precautions, protective equipment and emergency procedures.
    PRECAUTIONS_EQUIPMENT_PROCEDURES = enum.auto()
    # - (b) Environmental precautions.
    ENVIRONMENTAL_PRECAUTIONS = enum.auto()
    # - (c) Methods and material for containment and cleaning up.
    CONTAINMENT_CLEANUP = enum.auto()
    # Other information
    ACCIDENTAL_RELEASE_OTHER = enum.auto()

    # SECTION 7: Handling and storage
    # - (a) Precautions for safe handling
    HANDLING_PRECAUTIONS = enum.auto()
    # - (b) Conditions for safe storage, including any incompatibilities
    SAFE_STORAGE_CONDITIONS = enum.auto()
    # Other information
    HANDLING_AND_STORAGE_OTHER = enum.auto()

    # SECTION 8: Exposure controls/personal protection
    # - (a) Control parameters e.g. occupational exposure limit values or biological limit values.
    CONTROL_PARAMETERS = enum.auto()
    # - (b) Appropriate engineering controls.
    ENGINEERING_CONTROLS = enum.auto()
    # - (c) Individual protection measures, such as personal protective equipment.
    INDIVIDUAL_PROTECTION = enum.auto()
    # Other information
    EXPOSURE_CONTROL_OTHER = enum.auto()

    # SECTION 9: Physical and chemical properties
    # - Physical state
    PROP_PHYSICAL_STATE = enum.auto()
    # - Colour
    PROP_COLOUR = enum.auto()
    # - Odour
    PROP_ODOUR = enum.auto()
    # - Melting point/freezing point
    PROP_MELTING_FREEZING = enum.auto()
    # - Boiling point or initial boiling point and boiling range;
    PROP_BOILING_POINT = enum.auto()
    # - Flammability
    PROP_FLAMMABILITY = enum.auto()
    # - Lower and upper explosion limit/flammability limit
    PROP_EXPLOSION_FLAMMABILITY_LIMIT = enum.auto()
    # - Flash point
    PROP_FLASH_POINT = enum.auto()
    # - Auto-ignition temperature
    PROP_AUTO_IGNITION_TEMPERATURE = enum.auto()
    # - Decomposition temperatures
    PROP_DECOMPOSITION_TEMPERATURE = enum.auto()
    # - pH
    PROP_PH = enum.auto()
    # - Kinematic viscosity
    PROP_KINEMATIC_VISCOSITY = enum.auto()
    # - Solubility
    PROP_SOLUBILITY = enum.auto()
    # - Partition coefficient: n-octanol/water (log value)
    PROP_PARTITION_COEFFICIENT = enum.auto()
    # - Vapour pressure
    PROP_VAPOUR_PRESSURE = enum.auto()
    # - Density and/or relative density
    PROP_DENSITY = enum.auto()
    # - Relative vapour density
    PROP_VAPOUR_DENSITY = enum.auto()
    # - Particle characteristics
    PROP_PARTICLE_CHARACTERISTICS = enum.auto()
    # Other information
    PHYSICAL_AND_CHEMICAL_OTHER = enum.auto()

    # SECTION 10: Stability and reactivity
    # - (a) Reactivity
    REACTIVITY = enum.auto()
    # - (b) Chemical stability
    CHEMICAL_STABILITY = enum.auto()
    # - (c) Possibility of hazardous reactions
    HAZARDOUS_REACTIONS = enum.auto()
    # - (d) Conditions to avoid
    CONDITIONS_TO_AVOID = enum.auto()
    # - (e) Incompatible materials
    INCOMPATIBLE_MATERIALS = enum.auto()
    # - (f) Hazardous decomposition products
    DECOMPOSITION_PRODUCTS = enum.auto()
    # Other information
    STABILITY_AND_REACTIVITY_OTHER = enum.auto()

    # SECTION 11: Toxicological information
    # Concise but complete and comprehensible description of the various toxicological (health)
    # effects and the available data used to identify those effects, including:
    # - (a) Information on the likely routes of exposure
    #       (inhalation, ingestion, skin and eye contact)
    ROUTES_OF_EXPOSURE = enum.auto()
    # - (b) Symptoms related to the physical, chemical and toxicological characteristics.
    TOXICOLOGICAL_CHARACTERISTICS = enum.auto()
    # - (c) Delayed and immediate effects and also chronic effects from short- and long-term
    #       exposure
    EFFECTS_FROM_EXPOSURE = enum.auto()
    # - (d) Numerical measures of toxicity (such as acute toxicity estimates).
    MEASURES_OF_TOXICITY = enum.auto()
    # Other information
    TOXICOLOGICAL_OTHER = enum.auto()

    # SECTION 12: Ecological information
    # - (a) Ecotoxicity (aquatic and terrestrial, where available)
    ECOTOXICITY = enum.auto()
    # - (b) Persistence and degradability
    PERSISTENCE_DEGRADABILITY = enum.auto()
    # - (c) Bioaccumulative potential
    BIOACCUMULATIVE_POTENTIAL = enum.auto()
    # - (d) Mobility in soil
    MOBILITY_IN_SOIL = enum.auto()
    # - (e) Other adverse effects
    ECO_OTHER_ADVERSE_EFFECTS = enum.auto()
    # Other information
    ECOLOGICAL_OTHER = enum.auto()

    # SECTION 13: Disposal considerations
    # Description of waste residues and information on their safe handling and methods of disposal,
    # including the disposal of any contaminated packaging.
    # Other information
    DISPOSAL_OTHER = enum.auto()

    # SECTION 14: Transport information
    # - (a) UN number
    TRANSPORT_UN_NUMBER = enum.auto()
    # - (b) UN proper shipping name
    TRANSPORT_UN_SHIPPING_NAME = enum.auto()
    # - (c) Transport hazard class(es)
    TRANSPORT_HAZARD_CLASSES = enum.auto()
    # - (d) Packing group, if applicable
    TRANSPORT_PACKING_GROUP = enum.auto()
    # - (e) Environmental hazards (e.g.: Marine pollutant (Yes/No))
    TRANSPORT_ENVIRONMENTAL = enum.auto()
    # - (f) Transport in bulk according to IMO instruments
    TRANSPORT_IN_BULK = enum.auto()
    # - (g) Special precautions which a user needs to be aware of, or needs to comply with, in
    #       connection with transport or conveyance either within or outside their premises.
    TRANSPORT_PRECAUTIONS = enum.auto()
    # Other information
    TRANSPORT_OTHER = enum.auto()

    # SECTION 15: Regulatory information
    # Safety, health and environmental specific for the product in question.
    # Other information
    REGULATORY_OTHER = enum.auto()

    # SECTION 16: Other information
    # including information on preparation and revision of the SDS
    # Other information
    OTHER_OTHER = enum.auto()


class GhsSdsItemType(Enum):
    """Type of the specific data contained within a :class:`GhsSdsItem`. Subject to change."""
    # TODO may be changed in the future
    TEXT = enum.auto()
    FIELD = enum.auto()
    LIST = enum.auto()
    FIGURE_HAZARD = enum.auto()
    FIGURE_OTHER = enum.auto()


def child_string(child_iterable, heading="", indent="| ", direct_child_indent="|-") -> str:
    """Stringifies items in the iterable and joins them together into a string representation."""
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
