""" Mostly cribbed from the internet, but the key point is that we don't need any table-specific code in here.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db', echo=True) # convert_unicode=True
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

def load_db_from_files():
    init_db()
    for table_class in Base.__subclasses__():
        # for row in table_class.load_data():
        #     assert len(row['GEO_id']) == 20, "WHa? {}".format(len(row['GEO_id']))
        data = list(table_class.load_data())
        db_session.bulk_update_mappings(table_class, data)
    db_session.commit()









