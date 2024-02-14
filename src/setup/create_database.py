from dotenv import load_dotenv
import os
import sqlalchemy as sqla

# from src.data.save_unece_lcia_results_to_database import load_and_save_impact_data
# from src.orm.fill_regions import fill_regions
from src.orm.base import sql_alchemy_base


def create_new_database(drop_existing=False):
    
    load_dotenv()
    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

    engine = sqla.create_engine(sqla.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD
    ))
    if drop_existing is True:
        sql_alchemy_base.metadata.drop_all(bind=engine)

    sql_alchemy_base.metadata.create_all(bind=engine)

    # Fill unchanging data tables
    # fill_regions()  # Fill the regions table
    # load_and_save_impact_data()  # Fill the environmental impact data tables
    #

if __name__ == '__main__':
    create_new_database(drop_existing=False)