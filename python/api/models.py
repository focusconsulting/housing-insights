# coding: utf-8
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, Table, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class BuildingPermits(Base):
    __tablename__ = 'building_permits'

    x = Column(Numeric)
    y = Column(Numeric)
    objectid = Column(Text)
    dcrainternalnumber = Column(Text)
    issue_date = Column(DateTime)
    permit_id = Column(Text)
    permit_type_name = Column(Text)
    permit_subtype_name = Column(Text)
    permit_category_name = Column(Text)
    application_status_name = Column(Text)
    full_address = Column(Text)
    desc_of_work = Column(Text)
    ssl = Column(Text)
    zoning = Column(Text)
    permit_applicant = Column(Text)
    fee_type = Column(Text)
    fees_paid = Column(Numeric)
    owner_name = Column(Text)
    lastmodifieddate = Column(DateTime)
    city = Column(Text)
    state = Column(Text)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    xcoord = Column(Numeric)
    ycoord = Column(Numeric)
    zipcode = Column(Text)
    maraddressrepositoryid = Column(Text)
    dcstataddresskey = Column(Text)
    dcstatlocationkey = Column(Text)
    ward = Column(Text)
    anc = Column(Text)
    smd = Column(Text)
    district = Column(Text)
    psa = Column(Text)
    neighborhood_cluster = Column(Text)
    hotspot2006name = Column(Text)
    hotspot2005name = Column(Text)
    hotspot2004name = Column(Text)
    businessimprovementdistrict = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class Census(Base):
    __tablename__ = 'census'

    census_tract_desc = Column(Text)
    census_tract = Column(Text)
    total_population = Column(Integer)
    acs_lower_rent_quartile = Column(Integer)
    acs_median_rent = Column(Integer)
    acs_upper_rent_quartile = Column(Integer)
    state = Column(Text)
    county = Column(Text)
    tract = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class CensusMarginOfError(Base):
    __tablename__ = 'census_margin_of_error'

    census_tract_desc = Column(Text)
    census_tract = Column(Text)
    total_population = Column(Integer)
    acs_lower_rent_quartile = Column(Integer)
    acs_median_rent = Column(Integer)
    acs_upper_rent_quartile = Column(Integer)
    state = Column(Text)
    county = Column(Text)
    tract = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class Crime(Base):
    __tablename__ = 'crime'

    x = Column(Numeric)
    y = Column(Numeric)
    ccn = Column(Integer)
    report_date = Column(DateTime)
    shift = Column(Text)
    method = Column(Text)
    offense = Column(Text)
    block = Column(Text)
    xblock = Column(Numeric)
    yblock = Column(Numeric)
    ward = Column(Text)
    anc = Column(Text)
    district = Column(Text)
    psa = Column(Text)
    neighborhood_cluster = Column(Text)
    block_group = Column(Text)
    census_tract = Column(Text)
    voting_precinct = Column(Text)
    xcoord = Column(Numeric)
    ycoord = Column(Numeric)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    bid = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    objectid = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class DcTax(Base):
    __tablename__ = 'dc_tax'

    objectid = Column(Text)
    ssl = Column(Text)
    assessor_name = Column(Text)
    land_use_code = Column(Text)
    land_use_description = Column(Text)
    landarea = Column(Integer)
    property_address = Column(Text)
    otr_neighborhood_code = Column(Text)
    otr_neighborhood_name = Column(Text)
    owner_name_primary = Column(Text)
    careof_name = Column(Text)
    owner_address_line1 = Column(Text)
    owner_address_line2 = Column(Text)
    owner_address_citystzip = Column(Text)
    appraised_value_baseyear_land = Column(Integer)
    appraised_value_baseyear_bldg = Column(Integer)
    appraised_value_prior_land = Column(Integer)
    appraised_value_prior_impr = Column(Integer)
    appraised_value_prior_total = Column(Integer)
    appraised_value_current_land = Column(Integer)
    appraised_value_current_impr = Column(Integer)
    appraised_value_current_total = Column(Integer)
    phasein_value_current_land = Column(Integer)
    phasein_value_current_bldg = Column(Integer)
    vacant_use = Column(Boolean)
    homestead_description = Column(Text)
    tax_type_description = Column(Text)
    taxrate = Column(Numeric)
    mixed_use = Column(Text)
    owner_occupied_coop_units = Column(Integer)
    last_sale_price = Column(Integer)
    last_sale_date = Column(DateTime)
    deed_date = Column(DateTime)
    current_assessment_cap = Column(Integer)
    proposed_assessment_cap = Column(Integer)
    owner_name_secondary = Column(Text)
    address_id = Column(Text)
    lastmodifieddate = Column(Date)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


t_manifest = Table(
    'manifest', metadata,
    Column('status', Text),
    Column('load_date', DateTime),
    Column('include_flag', Text),
    Column('destination_table', Text),
    Column('unique_data_id', Text),
    Column('update_method', Text),
    Column('data_date', Date),
    Column('encoding', Text),
    Column('local_folder', Text),
    Column('s3_folder', Text),
    Column('filepath', Text),
    Column('notes', Text)
)


class Project(Base):
    __tablename__ = 'project'

    nlihc_id = Column(Text)
    mar_id = Column(Text)
    status = Column(Text)
    subsidized = Column(Text)
    cat_expiring = Column(Text)
    cat_failing_insp = Column(Text)
    proj_name = Column(Text)
    proj_addre = Column(Text)
    proj_city = Column(Text)
    proj_st = Column(Text)
    zip = Column(Text)
    proj_units_tot = Column(Numeric)
    proj_units_assist_min = Column(Integer)
    proj_units_assist_max = Column(Integer)
    hud_own_effect_dt = Column(Date)
    hud_own_name = Column(Text)
    hud_own_type = Column(Text)
    hud_mgr_name = Column(Text)
    hud_mgr_type = Column(Text)
    subsidy_start_first = Column(Date)
    subsidy_start_last = Column(Date)
    subsidy_end_first = Column(Date)
    subsidy_end_last = Column(Date)
    ward = Column(Text)
    pbca = Column(Text)
    anc = Column(Text)
    psa2012 = Column(Text)
    census_tract = Column(Text)
    neighborhood_cluster = Column(Text)
    neighborhood_cluster_desc = Column(Text)
    zip_string = Column(Text)
    proj_image_url = Column(Text)
    proj_streetview_url = Column(Text)
    proj_address_id = Column(Text)
    proj_x = Column(Numeric)
    proj_y = Column(Numeric)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    bldg_count = Column(Integer)
    update_dtm = Column(Text)
    subsidy_info_source_property = Column(Text)
    contract_number = Column(Text)
    category_code = Column(Text)
    cat_at_risk = Column(Text)
    cat_more_info = Column(Text)
    cat_lost = Column(Text)
    cat_replaced = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class ReacScore(Base):
    __tablename__ = 'reac_score'

    nlihc_id = Column(Text)
    reac_date = Column(Date)
    reac_score = Column(Text)
    reac_score_num = Column(Integer)
    reac_score_letter = Column(Text)
    reac_score_star = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class RealProperty(Base):
    __tablename__ = 'real_property'

    nlihc_id = Column(Text)
    ssl = Column(Text)
    rp_date = Column(Date)
    rp_type = Column(Text)
    rp_desc = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class Subsidy(Base):
    __tablename__ = 'subsidy'

    nlihc_id = Column(Text)
    subsidy_id = Column(Text)
    units_assist = Column(Integer)
    poa_start = Column(Date)
    poa_end = Column(Date)
    contract_number = Column(Text)
    rent_to_fmr_description = Column(Text)
    subsidy_active = Column(Boolean)
    subsidy_info_source_id = Column(Text)
    subsidy_info_source = Column(Text)
    subsidy_info_source_date = Column(Date)
    update_dtm = Column(Text)
    program = Column(Text)
    compl_end = Column(Date)
    poa_end_prev = Column(Date)
    agency = Column(Text)
    poa_start_orig = Column(Date)
    portfolio = Column(Text)
    subsidy_info_source_property = Column(Text)
    poa_end_actual = Column(Date)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class Topa(Base):
    __tablename__ = 'topa'

    unique_data_id = Column(Text)
    nidc_rcasd_id = Column(Text)
    notice_type = Column(Text)
    orig_address = Column(Text)
    notes = Column(Text)
    source_file = Column(Text)
    notice_date = Column(Text)
    num_units = Column(Integer)
    sale_price = Column(Integer)
    address = Column(Text)
    addr_num = Column(Integer)
    address_std = Column(Text)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    address_id = Column(Numeric)
    anc2002 = Column(Text)
    anc2012 = Column(Text)
    cluster_tr2000 = Column(Text)
    geo2000 = Column(Text)
    geo2010 = Column(Text)
    geobg2010 = Column(Text)
    geoblk2010 = Column(Text)
    psa2004 = Column(Text)
    psa2012 = Column(Text)
    ssl = Column(Text)
    voterpre2012 = Column(Text)
    ward2002 = Column(Text)
    ward = Column(Text)
    m_addr = Column(Text)
    m_city = Column(Text)
    m_state = Column(Text)
    m_zip = Column(Numeric)
    m_obs = Column(Numeric)
    dc_mar_geocode_matched = Column(Text)
    dc_mar_geocode_status = Column(Text)
    dc_mar_geocode_notes = Column(Text)
    dc_mar_geocode_score = Column(Integer)
    id = Column(Text, primary_key=True)


class WmataDist(Base):
    __tablename__ = 'wmata_dist'

    nlihc_id = Column(Text)
    type = Column(Text)
    stop_id_or_station_code = Column(Text)
    dist_in_miles = Column(Numeric)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)


class WmataInfo(Base):
    __tablename__ = 'wmata_info'

    stop_id_or_station_code = Column(Text)
    type = Column(Text)
    name = Column(Text)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    lines = Column(Text)
    unique_data_id = Column(Text)
    id = Column(Text, primary_key=True)
