from __future__ import annotations

import re
from typing import AnyStr

from tungsten.globally_harmonized_system.safety_data_sheet import (
    GhsSdsSectionTitle,
    GhsSdsSubsectionTitle
)
from tungsten.globally_harmonized_system.safety_data_sheet_rules import (
    GhsSdsRules,
    SubsectionDiscriminatorRules
)


class SigmaAldrichGhsSdsRules(GhsSdsRules):

    def get_section_identifier(self) -> list[re.Pattern[AnyStr]]:
        return [re.compile(r"([A-Z])+\s+\d?\d?:\s+[\w\s]+")]

    def get_section_discriminator(self) -> dict[re.Pattern[AnyStr], GhsSdsSectionTitle]:
        return {
            re.compile(r"SECTION\s1\D"): GhsSdsSectionTitle.IDENTIFICATION,
            re.compile(r"SECTION\s2\D"): GhsSdsSectionTitle.HAZARDS,
            re.compile(r"SECTION\s3\D"): GhsSdsSectionTitle.COMPOSITION,
            re.compile(r"SECTION\s4\D"): GhsSdsSectionTitle.FIRST_AID,
            re.compile(r"SECTION\s5\D"): GhsSdsSectionTitle.FIRE_FIGHTING,
            re.compile(r"SECTION\s6\D"): GhsSdsSectionTitle.ACCIDENTAL_RELEASE,
            re.compile(r"SECTION\s7\D"): GhsSdsSectionTitle.HANDLING_AND_STORAGE,
            re.compile(r"SECTION\s8\D"): GhsSdsSectionTitle.EXPOSURE_CONTROL,
            re.compile(r"SECTION\s9\D"): GhsSdsSectionTitle.PHYSICAL_AND_CHEMICAL,
            re.compile(r"SECTION\s10\D"): GhsSdsSectionTitle.STABILITY_AND_REACTIVITY,
            re.compile(r"SECTION\s11\D"): GhsSdsSectionTitle.TOXICOLOGICAL,
            re.compile(r"SECTION\s12\D"): GhsSdsSectionTitle.ECOLOGICAL,
            re.compile(r"SECTION\s13\D"): GhsSdsSectionTitle.DISPOSAL,
            re.compile(r"SECTION\s14\D"): GhsSdsSectionTitle.TRANSPORT,
            re.compile(r"SECTION\s15\D"): GhsSdsSectionTitle.REGULATORY,
            re.compile(r"SECTION\s16\D"): GhsSdsSectionTitle.OTHER
        }

    def get_subsection_identifier(self) -> list[re.Pattern[AnyStr]]:
        return [re.compile(r"(^\d?\d\.\d)\s+[\w\s]+$")]

    def get_subsection_discriminator(self) -> \
            dict[GhsSdsSectionTitle, SubsectionDiscriminatorRules]:
        # TODO figure out what Sigma-Aldrich uses for other GHS sections not specified currently.
        return {
            GhsSdsSectionTitle.IDENTIFICATION: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Product\sidentifiers)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.GHS_PRODUCT_IDENTIFIER,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.OTHER_MEANS_OF_IDENTIFICATION,
                    re.compile(r"(Relevant\sidentified\suses)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.RECOMMENDED_USE_AND_RESTRICTIONS,
                    re.compile(r"(Details\sof\sthe\ssupplier)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.SUPPLIER_DETAILS,
                    re.compile(r"(Emergency\stelephone)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.EMERGENCY_PHONE_NUMBER,
                },
                default=GhsSdsSubsectionTitle.IDENTIFICATION_OTHER
            ),
            GhsSdsSectionTitle.HAZARDS: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Classification\sof\sthe\ssubstance)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.GHS_SUBSTANCE_CLASSIFICATION,
                    re.compile(r"(GHS\sLabel\selements)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.GHS_LABEL_ELEMENTS,
                    re.compile(r"(Hazards\snot\sotherwise\sclassified)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.OTHER_HAZARDS
                },
                default=GhsSdsSubsectionTitle.HAZARDS_OTHER
            ),
            GhsSdsSectionTitle.COMPOSITION: SubsectionDiscriminatorRules(
                matching_rules={
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.SUBSTANCE_CHEMICAL_IDENTITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.SUBSTANCE_COMMON_NAME_SYNONYMS,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.SUBSTANCE_CAS_NUMBER_IDENTIFIERS,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.SUBSTANCE_IMPURITIES_ADDITIVES,
                    re.compile(r"(Mixtures)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.MIXTURE_INGREDIENTS
                },
                default=GhsSdsSubsectionTitle.COMPOSITION_OTHER
            ),
            GhsSdsSectionTitle.FIRST_AID: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Description\sof)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.FIRST_AID_MEASURES,
                    re.compile(r"(Most\simportant\ssymptoms)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.SYMPTOMS_AND_EFFECTS,
                    re.compile(r"(Indication\sof\sany\simmediate)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.INDICATION_MEDICAL_TREATMENT
                },
                default=GhsSdsSubsectionTitle.FIRST_AID_OTHER
            ),
            GhsSdsSectionTitle.FIRE_FIGHTING: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Extinguishing\smedia)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.EXTINGUISHING_MEDIA,
                    re.compile(r"(Special\shazards)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.SPECIAL_HAZARDS,
                    re.compile(r"(Advice\sfor\sfirefighters)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.FIREFIGHTER_EQUIPMENT_PRECAUTIONS
                },
                default=GhsSdsSubsectionTitle.FIRE_FIGHTING_OTHER
            ),
            GhsSdsSectionTitle.ACCIDENTAL_RELEASE: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Personal\sprecautions)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.PRECAUTIONS_EQUIPMENT_PROCEDURES,
                    re.compile(r"(Environmental\sprecautions)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.ENVIRONMENTAL_PRECAUTIONS,
                    re.compile(r"(Methods\sand\smaterials)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.CONTAINMENT_CLEANUP
                },
                default=GhsSdsSubsectionTitle.ACCIDENTAL_RELEASE_OTHER
            ),
            GhsSdsSectionTitle.HANDLING_AND_STORAGE: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Precautions\sfor\ssafe\shandling)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.HANDLING_PRECAUTIONS,
                    re.compile(r"(Conditions\sfor\ssafe\sstorage)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.SAFE_STORAGE_CONDITIONS
                },
                default=GhsSdsSubsectionTitle.HANDLING_AND_STORAGE_OTHER
            ),
            GhsSdsSectionTitle.EXPOSURE_CONTROL: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Control\sparameters)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.CONTROL_PARAMETERS,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.ENGINEERING_CONTROLS,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.INDIVIDUAL_PROTECTION
                },
                default=GhsSdsSubsectionTitle.EXPOSURE_CONTROL_OTHER
            ),
            GhsSdsSectionTitle.PHYSICAL_AND_CHEMICAL: SubsectionDiscriminatorRules(
                matching_rules={
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_PHYSICAL_STATE,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_COLOUR,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_ODOUR,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_MELTING_FREEZING,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_BOILING_POINT,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_FLAMMABILITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_EXPLOSION_FLAMMABILITY_LIMIT,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_FLASH_POINT,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_AUTO_IGNITION_TEMPERATURE,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_DECOMPOSITION_TEMPERATURE,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_PH,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_KINEMATIC_VISCOSITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_SOLUBILITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_PARTITION_COEFFICIENT,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_VAPOUR_PRESSURE,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_DENSITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_VAPOUR_DENSITY,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.PROP_PARTICLE_CHARACTERISTICS
                },
                default=GhsSdsSubsectionTitle.PHYSICAL_AND_CHEMICAL_OTHER
            ),
            GhsSdsSectionTitle.STABILITY_AND_REACTIVITY: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Reactivity)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.REACTIVITY,
                    re.compile(r"(Chemical\sstability)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.CHEMICAL_STABILITY,
                    re.compile(r"(Possibility\sof\shazardous\sreactions)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.HAZARDOUS_REACTIONS,
                    re.compile(r"(Conditions\sto\savoid)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.CONDITIONS_TO_AVOID,
                    re.compile(r"(Incompatible\smaterials)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.INCOMPATIBLE_MATERIALS,
                    re.compile(r"(Hazardous\sdecomposition)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.DECOMPOSITION_PRODUCTS
                },
                default=GhsSdsSubsectionTitle.STABILITY_AND_REACTIVITY_OTHER
            ),
            GhsSdsSectionTitle.TOXICOLOGICAL: SubsectionDiscriminatorRules(
                matching_rules={
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.ROUTES_OF_EXPOSURE,
                    re.compile(r"(toxicological\seffects)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.TOXICOLOGICAL_CHARACTERISTICS,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.EFFECTS_FROM_EXPOSURE,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.MEASURES_OF_TOXICITY
                },
                default=GhsSdsSubsectionTitle.TOXICOLOGICAL_OTHER
            ),
            GhsSdsSectionTitle.ECOLOGICAL: SubsectionDiscriminatorRules(
                matching_rules={
                    re.compile(r"(Toxicity)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.ECOTOXICITY,
                    re.compile(r"(Persistence\sand\sdegradability)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.PERSISTENCE_DEGRADABILITY,
                    re.compile(r"(Bioaccumulative)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.BIOACCUMULATIVE_POTENTIAL,
                    re.compile(r"(Mobility\sin\ssoil)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.MOBILITY_IN_SOIL,
                    re.compile(r"(Other\sadverse\seffects)", re.IGNORECASE):
                        GhsSdsSubsectionTitle.ECO_OTHER_ADVERSE_EFFECTS
                },
                default=GhsSdsSubsectionTitle.ECOLOGICAL_OTHER
            ),
            GhsSdsSectionTitle.DISPOSAL: SubsectionDiscriminatorRules(
                matching_rules={
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.DISPOSAL_OTHER
                },
                default=GhsSdsSubsectionTitle.DISPOSAL_OTHER
            ),
            GhsSdsSectionTitle.TRANSPORT: SubsectionDiscriminatorRules(
                matching_rules={
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_UN_NUMBER,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_UN_SHIPPING_NAME,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_HAZARD_CLASSES,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_PACKING_GROUP,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_ENVIRONMENTAL,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_IN_BULK,
                    # re.compile(r"", re.IGNORECASE):
                    #     GhsSdsSubsectionTitle.TRANSPORT_PRECAUTIONS
                },
                default=GhsSdsSubsectionTitle.TRANSPORT_OTHER
            ),
            GhsSdsSectionTitle.REGULATORY: SubsectionDiscriminatorRules(
                matching_rules={},
                default=GhsSdsSubsectionTitle.REGULATORY_OTHER
            ),
            GhsSdsSectionTitle.OTHER: SubsectionDiscriminatorRules(
                matching_rules={},
                default=GhsSdsSubsectionTitle.OTHER_OTHER
            )
        }
