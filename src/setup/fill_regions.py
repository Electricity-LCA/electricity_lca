"""
Fill Regions table with countries defined in ENTSO-E
"""
import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from entsoe.mappings import Area


def fill_regions():
    """Fill a Regions table in the SQL database using the bidding zones named in entsoe.mappings.Areas"""
    bidding_zones = [x.name for x in Area]

    load_dotenv()
    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

    # Connect to postgres database
    sql_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD
    ))

    countries_df = pd.DataFrame({'Code': bidding_zones,'Type':'Bidding zone','Description':None})
    countries_df = countries_df.reset_index()
    countries_df = countries_df.rename({'index':'Id'},axis=1)
    countries_df.to_sql('Regions',sql_engine, if_exists='append',index=False)


if __name__ == '__main__':
    fill_regions()
