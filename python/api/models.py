from base import Base, Column, Text, Integer, Float, relationship, ForeignKey


class MedianRent(Base):
    __tablename__ = 'acs_rent_median'

    tract_id = Column('geo_id2', Text, ForeignKey('census_mapping.acs_code'), primary_key=True)
    median_rent = Column('median_rent', Integer)

    tract = relationship("CensusMapping", uselist=False, backref='median_rent')


class Project(Base):
    __tablename__ = 'project'

    nlihc_id = Column('nlihc_id', Text, primary_key=True)
#   total_units = db.Column('proj_units_tot', Integer)
    min_assisted_units = Column('proj_units_assist_min', Integer)
    latitude = Column('proj_lat', Float)
    longitude = Column('proj_lon', Float)


class CensusMapping(Base):
    __tablename__ = 'census_mapping'

    acs_code = Column('acs_code', Text, primary_key=True)
    tract_code = Column('tract_code', Text)

class 