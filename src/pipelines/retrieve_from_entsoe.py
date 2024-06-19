import logging
import os
import sys

import pandas as pd
import dotenv
import sqlalchemy
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
import time

from src.data.get_common_data import load_common_data_from_db
import argparse

from src.pipelines.get_and_store_generation_data import get_and_store_generation_for_region

# TODO: Move mapping to the database
generation_type_to_id_mapping = {
    ('Fossil Hard coal', 'Actual Aggregated'): 1
}

# Logging
logging.basicConfig(level=logging.DEBUG, filename='data_loader.log', format='%(asctime)s: %(message)s')


# logging.addHandler(logging.FileHandler('data_loader.log'))

def my_handler(type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))


sys.excepthook = my_handler


def main(start, end, sleep_time_between_requests=1):
    dotenv.load_dotenv()

    start_timestamp = pd.Timestamp(start, tz='Europe/Brussels')
    end_timestamp = pd.Timestamp(end, tz='Europe/Brussels')
    if (start_timestamp == pd.NaT) or (end_timestamp == pd.NaT):
        logging.error("Start or end datestamp is not correctly formed or invalid")
    generation_type_filter = None  # [('Fossil Hard coal', 'Actual Aggregated')]

    load_dotenv()
    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')
    PORT = os.getenv('ELEC_LCA_DB_PORT')
    ENTOSE_SECURITY_TOKEN = os.environ.get('ENTSOE_SECURITY_TOKEN')

    # Connect to postgres database
    sql_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD,
        port=PORT
    ))
    cache = load_common_data_from_db(sql_engine)

    generation_types = cache.generation_types

    regions = cache.regions

    client = EntsoePandasClient(api_key=ENTOSE_SECURITY_TOKEN)

    s = time.time()
    for _, region_code in regions['Code'].items():
        get_and_store_generation_for_region(entsoe_client=client, sql_engine=sql_engine, region_code=region_code,
                                            start=start_timestamp, end=end_timestamp, cache=cache,
                                            generation_type_filter=generation_type_filter)
        time.sleep(sleep_time_between_requests)
    e = time.time()
    logging.info(f'{e - s:.2f} s to retrieve and store data for {len(regions)} regions')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("entsoe_pipeline_live",
                                     description="Retrieve electricity generation data from ENTSO-E and store to a postgres database")
    parser.add_argument('-s','--start', help="The start date or datestamp (in the form yyyymmdd)")
    parser.add_argument('-e','--end', help="The end date or datestamp (in the form yyyymmdd)")
    parser.add_argument('--sleep_time_between_requests',
                        help="Time in seconds between sending requests to ENTSO-E",required=False)
    args = parser.parse_args()
    print('Arguments: ',args)
    main(start=args.start,end=args.end,sleep_time_between_requests=args.sleep_time_between_requests)
