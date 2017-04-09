from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    String,
    Date,
    ForeignKeyConstraint,
)
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship, reconstructor, validates
from sqlalchemy.orm.collections import attribute_mapped_collection

Base = declarative_base()


class ACSRent():

    geo_id = Column(
        "geo_id",
        Text,
        info={
            "display_name": "geo_id",
            "display_text": "",
            "source_name": "GEO.id"
        }
    )

    geo_id2 = Column(
        "geo_id2",
        Text,
        info={
            "display_name": "geo_id2",
            "display_text": "",
            "source_name": "GEO.id2"
        }
    )

    geo_display_label = Column(
        "geo_display_label",
        Text,
        info={
            "display_name": "geo_display_label",
            "display_text": "",
            "source_name": "GEO.display-label"
        }
    )


class ACSRentLower(Base, ACSRent):
    __table_name__ = 'acs_rent_lower'
    CLEANER = "ACSRentCleaner"
    REPLACE_TABLE = False

    lower_quartile_rent = Column(
        "lower_quartile_rent",
        Integer,
        info={
            "display_name": "Lower quartile rent (ACS)",
            "display_text": "Lower quartile rent from the American Community Survey table B25057",
            "source_name": "HD01_VD01"
        }
    )
    

class ACSRentMedian(Base, ACSRent):
    __table_name__ = "acs_rent_median"
    CLEANER ="ACSRentCleaner"
    REPLACE_TABLE = False

    median_rent = Column(
        "median_rent",
        Integer,
        info={
            "display_name": "Median Rent (ACS)",
            "display_text": "Median rent from the American Community Survey table B25058",
            "source_name": "HD01_VD01"
        }
    )

    median_rent_moe = Column(
        "median_rent_moe",
        Integer,
        info={
            "display_name": "Margin of error",
            "display_text": "",
            "source_name": "HD02_VD01"
        }
    )

class ACERentUpper(Base, ACSRent):
    __table_name__ = "acs_rent_upper"
    CLEANER = "ACSRentCleaner"
    REPLACE_TABLE = False

    upper_quartile_rent = Column(
        "upper_quartile_rent",
        Integer,
        info={
                "display_name": "Upper quartile rent (ACS)",
                "display_text": "Upper quartile rent from the American Community Survey table B25059",
                "source_name": "HD01_VD01",
        }
    )

    upper_quartile_rent_moe = Column(
        "upper_quartile_rent_moe",
        Integer,
        info={
                "display_name": "Margin of error",
                "display_text": "",
                "source_name": "HD02_VD01",
        }
    )

class CensusMapping(Base):
    __table_name__ = "census_mapping"
    CLEANER = "GenericCleaner"
    REPLACE_TABLE = True

    acs_code = Column(
        "acs_code",
        Text,            
        info={
            "display_name": "acs_code",
            "display_text": "",
            "source_name": "acs_code",
        }
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


class Project(Base):
    __table_name__ = "project"
    CLEANER = "ProjectCleaner"
    REPLACE_TABLE = True

    nlihc_id = Column(        
        "nlihc_id",
        Text,
        info={
                "display_name": "nlihc_id",
                "display_text": "",
                "source_name": "Nlihc_id",
        }
    )
    
    status = Column(
        "status",
        Text,
        info={
                "display_name": "status",
                "display_text": "",
                "source_name": "Status",
            }
    )

    subsidized = Column(
        "subsidized",
        Text,
        info={
                "display_name": "subsidized",
                "display_text": "",
                "source_name": "Subsidized",
        }
    )

    cat_expiring = Column(
        "cat_expiring",
        Text,
        info={
                "display_name": "cat_expiring",
                "display_text": "",
                "source_name": "Cat_Expiring",
        }
    )

    cat_failing_insp = Column(
        "cat_failing_insp",
        Text,
        info={
                "display_name": "cat_failing_insp",
                "display_text": "",
                "source_name": "Cat_Failing_Insp",
        }
    )

    proj_name = Column(
        "proj_name",
        Text,
        info={
                "display_name": "proj_name",
                "display_text": "",
                "source_name": "Proj_Name",
        }
    )

    proj_addre = Column(
        "proj_addre",
        Text,
        info={
                "display_name": "proj_addre",
                "display_text": "",
                "source_name": "Proj_Addre",
        }
    )

    proj_city = Column(
        "proj_city",
        Text,
        info={
                "display_name": "proj_city",
                "display_text": "",
                "source_name": "Proj_City",
        }
    )

    proj_st = Column(
        "proj_st",
        Text,
        info={
                "display_name": "proj_st",
                "display_text": "",
                "source_name": "Proj_ST",
        }
    )

    proj_zip = Column(
        "proj_zip",
        Text,
        info={
                "display_name": "proj_zip",
                "display_text": "",
                "source_name": "Proj_Zip",
        }
    )

    proj_units_tot = Column(
        "proj_units_tot",
        Decimal,
        info={
                "display_name": "proj_units_tot",
                "display_text": "",
                "source_name": "Proj_Units_Tot",
        }
    )

    proj_units_assist_min = Column(
        "proj_units_assist_min",
        Text,
        info={
                "display_name": "proj_units_assist_min",
                "display_text": "",
                "source_name": "Proj_Units_Assist_Min",
        }
    )

    proj_units_assist_max = Column(
        "proj_units_assist_max",
        Text,
        info={
                "display_name": "proj_units_assist_max",
                "display_text": "",
                "source_name": "Proj_Units_Assist_Max",
        }
    )

    hud_own_effect_dt = Column(
        "hud_own_effect_dt",
        Date,
        info={
                "display_name": "hud_own_effect_dt",
                "display_text": "",
                "source_name": "Hud_Own_Effect_dt",
        }
    )

    hud_own_name = Column(
        "hud_own_name",
        Text,
        info={
                "display_name": "hud_own_name",
                "display_text": "",
                "source_name": "Hud_Own_Name",
        }
    )

    hud_own_type = Column(
        "hud_own_type",
        Text,
        info={
                "display_name": "hud_own_type",
                "display_text": "",
                "source_name": "Hud_Own_Type",
        }
    )

    hud_mgr_name = Column(
        "hud_mgr_name",
        Text,
        info={
                "display_name": "hud_mgr_name",
                "display_text": "",
                "source_name": "Hud_Mgr_Name",
        }
    )

    hud_mgr_type = Column(
        "hud_mgr_type",
        Text,,
        info={
                "display_name": "hud_mgr_type",
                "display_text": "",
                "source_name": "Hud_Mgr_Type",
        }
    )

    subsidy_start_first = Column(
        "subsidy_start_first",
        Date,
        info={
                "display_name": "subsidy_start_first",
                "display_text": "",
                "source_name": "Subsidy_Start_First",
        }
    )

    subsidy_start_last = Column(
        "subsidy_start_last",
        Date,
        info={
                "display_name": "subsidy_start_last",
                "display_text": "",
                "source_name": "Subsidy_Start_Last",
        }
    )

    subsidy_end_first = Column(
        "subsidy_end_first",
        Date,
        info={
                "display_name": "subsidy_end_first",
                "display_text": "",
                "source_name": "Subsidy_End_First",
        }
    )

    subsidy_end_last = Column(
        "subsidy_end_last",
        Date,
        info={
                "display_name": "subsidy_end_last",
                "display_text": "",
                "source_name": "Subsidy_End_Last",
        }
    )

    ward2012 = Column(
        "ward2012",
        Text,
        info={
                "display_name": "ward2012",
                "display_text": "",
                "source_name": "Ward2012",
        }
    )

    pbca = Column(
        "pbca",
        Text,
        info={
                "display_name": "pbca",
                "display_text": "",
                "source_name": "PBCA",
        }
    )

    anc2012 = Column(
        "anc2012",
        Text,
        info={
                "display_name": "anc2012",
                "display_text": "",
                "source_name": "Anc2012",
        }
    )

    psa2012 = Column(
        "psa2012",
        Text,
        info={
                "display_name": "psa2012",
                "display_text": "",
                "source_name": "Psa2012",
        }
    )

    geo2010 = Column(
        "geo2010",
        Text,
        info={
                "display_name": "geo2010",
                "display_text": "",
                "source_name": "Geo2010",
        }
    )

    cluster_tr2000 = Column(
        "cluster_tr2000",
        Text,
        info={
                "display_name": "cluster_tr2000",
                "display_text": "",
                "source_name": "Cluster_tr2000",
        }
    )

    cluster_tr2000_name = Column(
        "cluster_tr2000_name",
        Text,
        info={
                "display_name": "cluster_tr2000_name",
                "display_text": "",
                "source_name": "Cluster_tr2000_name",
        }
    )

    zip_code = Column(
        "zip",
        Text,
        info={
                "display_name": "zip",
                "display_text": "",
                "source_name": "Zip",
        }
    )

    proj_image_url = Column(
        "proj_image_url",
        Text,
        info={
                "display_name": "proj_image_url",
                "display_text": "",
                "source_name": "Proj_image_url",
        }
    )

    proj_streetview_url = Column(
        "proj_streetview_url",
        Text,
        info={
                "display_name": "proj_streetview_url",
                "display_text": "",
                "source_name": "Proj_streetview_url",
        }
    )

    proj_address_id = Column(
        "proj_address_id",
        Text,
        info={
                "display_name": "proj_address_id",
                "display_text": "",
                "source_name": "Proj_address_id",
        }
    )

    proj_x = Column(
        "proj_x",
        Decimal,
        info={
                "display_name": "proj_x",
                "display_text": "",
                "source_name": "Proj_x",
        }
    )

    proj_y = Column(
        "proj_y",
        Decimal,
        info={
                "display_name": "proj_y",
                "display_text": "",
                "source_name": "Proj_y",
        }
    )

    proj_lat = Column(
        "proj_lat",
        Decimal,
        info={
                "display_name": "proj_lat",
                "display_text": "",
                "source_name": "Proj_lat",
        }
    )

    proj_lon = Column(
        "proj_lon",
        Decimal,
        info={
                "display_name": "proj_lon",
                "display_text": "",
                "source_name": "Proj_lon",
        }
    )

    bldg_count = Column(
        "bldg_count",
        Integer,
        info={
                "display_name": "bldg_count",
                "display_text": "",
                "source_name": "Bldg_count",
        }
    )

    update_dtm = Column(
        "update_dtm",
        Text,
        info={
                "display_name": "update_dtm",
                "display_text": "",
                "source_name": "Update_Dtm",
        }
    )

    subsidy_info_source_property = Column(
        "subsidy_info_source_property",
        Text,
        info={
                "display_name": "subsidy_info_source_property",
                "display_text": "",
                "source_name": "Subsidy_info_source_property",
        }
    )

    contract_number = Column(
        "contract_number",
        Text,
        info={
                "display_name": "contract_number",
                "display_text": "",
                "source_name": "contract_number",
        }
    )

    category_code = Column(
        "category_code",
        Text,
        info={
                "display_name": "category_code",
                "display_text": "",
                "source_name": "Category_Code",
        }
    )

    cat_at_risk = Column(
        "cat_at_risk",
        Text,
        info={
                "display_name": "cat_at_risk",
                "display_text": "",
                "source_name": "Cat_At_Risk",
        }
    )

    cat_more_info = Column(
        "cat_more_info",
        Text,
        info={
                "display_name": "cat_more_info",
                "display_text": "",
                "source_name": "Cat_More_Info",
        }
    )

    cat_lost = Column(
        "cat_lost",
        Text,
        info={
                "display_name": "cat_lost",
                "display_text": "",
                "source_name": "Cat_Lost",
        }
    )

    cat_replaced = Column(
        "cat_replaced",
        Text,
        info={
                "display_name": "cat_replaced",
                "display_text": "",
                "source_name": "Cat_Replaced",
        }
    )
