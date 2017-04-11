from .mixins.Ingestible import MultipleFileIngestible
from database import Base
from sqlalchemy import Column, Text, Integer, String

class ACSRent(MultipleFileIngestible):
    """ Abstract class for ACS Rent tables.
    """

    NOTES = "Ready to go data at the census tract level. Do pay attention to margins of error"
    YEAR_RANGE = range(2009, 2016)
    YEAR_RANGE_FIELD = "DATA_YEAR"
    ROW_OFFSET = 1  # This is annoying

    @classmethod
    def get_file_paths(cls):
        return [
            cls.FILE_PATH.format(
                year,
                str(year)[-2:]
            )
            for year in cls.YEAR_RANGE
        ]


    geo_id = Column(
        "GEO_id",
        Text,
        #primary_key=True,
        info={
            "display_name": "geo_id",
            "display_text": "",
            "source_name": "GEO.id"
        }
    )

    geo_id2 = Column(
        "GEO_id2",
        Integer,
        primary_key=True,
        nullable=False,
        info={
            "display_name": "geo_id2",
            "display_text": "",
            "source_name": "GEO.id2"
        }
    )

    geo_display_label = Column(
        "GEO_display-label",
        Text,
        info={
            "display_name": "geo_display_label",
            "display_text": "",
            "source_name": "GEO.display-label"
        }
    )

    data_year = Column(
        "DATA_YEAR",
        Integer,
        primary_key=True,
        nullable=False
    )




class ACSRentLower(Base, ACSRent):
    """ ACS table for lower quintile of rent.  Concrete class.
    """
    __tablename__ = 'acs_rent_lower'
    CLEANER = "ACSRentCleaner"
    REPLACE_TABLE = False
    FILE_PATH = "raw/acs/B25057_lower_rent_by_tract/{}_5year/ACS_{}_5YR_B25057_with_ann.csv"


    lower_quartile_rent = Column(
        "HD01_VD01",
        Integer,
        info={
            "display_name": "Lower quartile rent (ACS)",
            "display_text": "Lower quartile rent from the American Community Survey table B25057",
            "source_name": "HD01_VD01"
        }
    )
    

class ACSRentMedian(Base, ACSRent):
    """ ACS table for median rent.  Concrete class.
    """
    __tablename__ = "acs_rent_median"
    CLEANER ="ACSRentCleaner"
    REPLACE_TABLE = False
    FILE_PATH = "raw/acs/B25058_median_rent_by_tract/{}_5year/ACS_{}_5YR_B25058_with_ann.csv"

    median_rent = Column(
        "HD01_VD01",
        Integer,
        info={
            "display_name": "Median Rent (ACS)",
            "display_text": "Median rent from the American Community Survey table B25058",
            "source_name": "HD01_VD01"
        }
    )

    median_rent_moe = Column(
        "HD02_VD01",
        Integer,
        info={
            "display_name": "Margin of error",
            "display_text": "",
            "source_name": "HD02_VD01"
        }
    )


class ACSRentUpper(Base, ACSRent):
    """ ACS table for upper quartile rent.  Concrete class.
    """
    __tablename__ = "acs_rent_upper"
    CLEANER = "ACSRentCleaner"
    REPLACE_TABLE = False
    FILE_PATH = "raw/acs/B25059_upper_rent_by_tract/{}_5year/ACS_{}_5YR_B25059_with_ann.csv"

    upper_quartile_rent = Column(
        "HD01_VD01",
        Integer,
        info={
                "display_name": "Upper quartile rent (ACS)",
                "display_text": "Upper quartile rent from the American Community Survey table B25059",
                "source_name": "HD01_VD01",
        }
    )

    upper_quartile_rent_moe = Column(
        "HD02_VD01",
        Integer,
        info={
                "display_name": "Margin of error",
                "display_text": "",
                "source_name": "HD02_VD01",
        }
    )
