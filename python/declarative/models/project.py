from sqlalchemy import Column, Integer, Float, Date, Text
from sqlalchemy.orm import validates
from .mixins.Ingestible import Ingestible
from database import Base

class Project(Base, Ingestible):
    __tablename__ = "project"
    CLEANER = "ProjectCleaner"
    REPLACE_TABLE = True
    FILE_PATH = "raw/preservation_catalog/20160401/Project.csv"

    @validates()
    def replace_nulls():
        raise NotImplementedError

    @validates()
    def parse_dates():
        raise NotImplementedError

    nlihc_id = Column(        
        "Nlihc_id",
        Text,
        info={
                "display_name": "nlihc_id",
                "display_text": "",
                "source_name": "Nlihc_id",
        },
    )
    
    status = Column(
        "Status",
        Text,
        info={
                "display_name": "status",
                "display_text": "",
                "source_name": "Status",
            }
    )

    subsidized = Column(
        "Subsidized",
        Text,
        info={
                "display_name": "subsidized",
                "display_text": "",
                "source_name": "Subsidized",
        }
    )

    cat_expiring = Column(
        "Cat_Expiring",
        Text,
        info={
                "display_name": "cat_expiring",
                "display_text": "",
                "source_name": "Cat_Expiring",
        }
    )

    cat_failing_insp = Column(
        "Cat_Failing_Insp",
        Text,
        info={
                "display_name": "cat_failing_insp",
                "display_text": "",
                "source_name": "Cat_Failing_Insp",
        }
    )

    proj_name = Column(
        "Proj_Name",
        Text,
        info={
                "display_name": "proj_name",
                "display_text": "",
                "source_name": "Proj_Name",
        }
    )

    proj_addre = Column(
        "Proj_Addre",
        Text,
        info={
                "display_name": "proj_addre",
                "display_text": "",
                "source_name": "Proj_Addre",
        }
    )

    proj_city = Column(
        "Proj_City",
        Text,
        info={
                "display_name": "proj_city",
                "display_text": "",
                "source_name": "Proj_City",
        }
    )

    proj_st = Column(
        "Proj_ST",
        Text,
        info={
                "display_name": "proj_st",
                "display_text": "",
                "source_name": "Proj_ST",
        }
    )

    proj_zip = Column(
        "Proj_Zip",
        Text,
        info={
                "display_name": "proj_zip",
                "display_text": "",
                "source_name": "Proj_Zip",
        }
    )

    proj_units_tot = Column(
        "Proj_Units_Tot",
        Float,
        info={
                "display_name": "proj_units_tot",
                "display_text": "",
                "source_name": "Proj_Units_Tot",
        }
    )

    proj_units_assist_min = Column(
        "Proj_Units_Assist_Min",
        Text,
        info={
                "display_name": "proj_units_assist_min",
                "display_text": "",
                "source_name": "Proj_Units_Assist_Min",
        }
    )

    proj_units_assist_max = Column(
        "Proj_Units_Assist_Max",
        Text,
        info={
                "display_name": "proj_units_assist_max",
                "display_text": "",
                "source_name": "Proj_Units_Assist_Max",
        }
    )

    hud_own_effect_dt = Column(
        "Hud_Own_Effect_dt",
        Date,
        info={
                "display_name": "hud_own_effect_dt",
                "display_text": "",
                "source_name": "Hud_Own_Effect_dt",
        }
    )

    hud_own_name = Column(
        "Hud_Own_Name",
        Text,
        info={
                "display_name": "hud_own_name",
                "display_text": "",
                "source_name": "Hud_Own_Name",
        }
    )

    hud_own_type = Column(
        "Hud_Own_Type",
        Text,
        info={
                "display_name": "hud_own_type",
                "display_text": "",
                "source_name": "Hud_Own_Type",
        }
    )

    hud_mgr_name = Column(
        "Hud_Mgr_Name",
        Text,
        info={
                "display_name": "hud_mgr_name",
                "display_text": "",
                "source_name": "Hud_Mgr_Name",
        }
    )

    hud_mgr_type = Column(
        "Hud_Mgr_Type",
        Text,
        info={
                "display_name": "hud_mgr_type",
                "display_text": "",
                "source_name": "Hud_Mgr_Type",
        }
    )

    subsidy_start_first = Column(
        "Subsidy_Start_First",
        Date,
        info={
                "display_name": "subsidy_start_first",
                "display_text": "",
                "source_name": "Subsidy_Start_First",
        }
    )

    subsidy_start_last = Column(
        "Subsidy_Start_Last",
        Date,
        info={
                "display_name": "subsidy_start_last",
                "display_text": "",
                "source_name": "Subsidy_Start_Last",
        }
    )

    subsidy_end_first = Column(
        "Subsidy_End_First",
        Date,
        info={
                "display_name": "subsidy_end_first",
                "display_text": "",
                "source_name": "Subsidy_End_First",
        }
    )

    subsidy_end_last = Column(
        "Subsidy_End_Last",
        Date,
        info={
                "display_name": "subsidy_end_last",
                "display_text": "",
                "source_name": "Subsidy_End_Last",
        }
    )

    ward2012 = Column(
        "Ward2012",
        Text,
        info={
                "display_name": "ward2012",
                "display_text": "",
                "source_name": "Ward2012",
        }
    )

    pbca = Column(
        "PBCA",
        Text,
        info={
                "display_name": "pbca",
                "display_text": "",
                "source_name": "PBCA",
        }
    )

    anc2012 = Column(
        "Anc2012",
        Text,
        info={
                "display_name": "anc2012",
                "display_text": "",
                "source_name": "Anc2012",
        }
    )

    psa2012 = Column(
        "Psa2012",
        Text,
        info={
                "display_name": "psa2012",
                "display_text": "",
                "source_name": "Psa2012",
        }
    )

    geo2010 = Column(
        "Geo2010",
        Text,
        info={
                "display_name": "geo2010",
                "display_text": "",
                "source_name": "Geo2010",
        }
    )

    cluster_tr2000 = Column(
        "Cluster_tr2000",
        Text,
        info={
                "display_name": "cluster_tr2000",
                "display_text": "",
                "source_name": "Cluster_tr2000",
        }
    )

    cluster_tr2000_name = Column(
        "Cluster_tr2000_name",
        Text,
        info={
                "display_name": "cluster_tr2000_name",
                "display_text": "",
                "source_name": "Cluster_tr2000_name",
        }
    )

    zip_code = Column(
        "Zip",
        Text,
        info={
                "display_name": "zip",
                "display_text": "",
                "source_name": "Zip",
        }
    )

    proj_image_url = Column(
        "Proj_image_url",
        Text,
        info={
                "display_name": "proj_image_url",
                "display_text": "",
                "source_name": "Proj_image_url",
        }
    )

    proj_streetview_url = Column(
        "Proj_streetview_url",
        Text,
        info={
                "display_name": "proj_streetview_url",
                "display_text": "",
                "source_name": "Proj_streetview_url",
        }
    )

    proj_address_id = Column(
        "Proj_address_id",
        Text,
        info={
                "display_name": "proj_address_id",
                "display_text": "",
                "source_name": "Proj_address_id",
        }
    )

    proj_x = Column(
        "Proj_x",
        Float,
        info={
                "display_name": "proj_x",
                "display_text": "",
                "source_name": "Proj_x",
        }
    )

    proj_y = Column(
        "Proj_y",
        Float,
        info={
                "display_name": "proj_y",
                "display_text": "",
                "source_name": "Proj_y",
        }
    )

    proj_lat = Column(
        "Proj_lat",
        Float,
        info={
                "display_name": "proj_lat",
                "display_text": "",
                "source_name": "Proj_lat",
        }
    )

    proj_lon = Column(
        "Proj_lon",
        Float,
        info={
                "display_name": "proj_lon",
                "display_text": "",
                "source_name": "Proj_lon",
        }
    )

    bldg_count = Column(
        "Bldg_count",
        Integer,
        info={
                "display_name": "bldg_count",
                "display_text": "",
                "source_name": "Bldg_count",
        }
    )

    update_dtm = Column(
        "Update_Dtm",
        Text,
        info={
                "display_name": "update_dtm",
                "display_text": "",
                "source_name": "Update_Dtm",
        }
    )

    subsidy_info_source_property = Column(
        "Subsidy_info_source_property",
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
        "Category_Code",
        Text,
        info={
                "display_name": "category_code",
                "display_text": "",
                "source_name": "Category_Code",
        }
    )

    cat_at_risk = Column(
        "Cat_At_Risk",
        Text,
        info={
                "display_name": "cat_at_risk",
                "display_text": "",
                "source_name": "Cat_At_Risk",
        }
    )

    cat_more_info = Column(
        "Cat_More_Info",
        Text,
        info={
                "display_name": "cat_more_info",
                "display_text": "",
                "source_name": "Cat_More_Info",
        }
    )

    cat_lost = Column(
        "Cat_Lost",
        Text,
        info={
                "display_name": "cat_lost",
                "display_text": "",
                "source_name": "Cat_Lost",
        }
    )

    cat_replaced = Column(
        "Cat_Replaced",
        Text,
        info={
                "display_name": "cat_replaced",
                "display_text": "",
                "source_name": "Cat_Replaced",
        }
    )
