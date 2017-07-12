from .mixins.Ingestible import Ingestible
from database import Base
from sqlalchemy import Column, Text

class CensusMapping(Base, Ingestible):
    __tablename__ = "census_mapping"
    CLEANER = "GenericCleaner"
    REPLACE_TABLE = True
    FILE_PATH = "raw/geographic_data/census_tract_mapping/DC_census_tract_crosswalk.csv"
    NOTES = "Created manually based on a crosswalk downloaded from census"

    acs_code = Column(
        "acs_code",
        Text,            
        info={
            "display_name": "acs_code",
            "display_text": "",
            "source_name": "acs_code",
        },
        primary_key=True
    )

    acs_remove_state_county = Column(
        "acs_remove_state_county",
        Text,
        info={
            "display_name": "acs_remove_state_county",
            "display_text": "acs_code stripped of its duplicative state and county codes",
            "source_name": "acs_remove_state_county",
        }
    )

    tract_code = Column(
        "tract_code",
        Text,
        info={
            "display_name": "tract_code",
            "display_text": "",
            "source_name": "tract_code",
        }
    )

    prescat_code = Column(
        "prescat_code",
        Text,
        info={
            "display_name": "prescat_code",
            "display_text": "",
            "source_name": "prescat_code",
        }
    )
