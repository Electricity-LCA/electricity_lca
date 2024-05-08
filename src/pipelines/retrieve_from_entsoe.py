import logging
import os
import pprint
import sys
from typing import List, Tuple

import pandas as pd
import dotenv
import requests.exceptions
import sqlalchemy
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
from entsoe.exceptions import NoMatchingDataError
import time

from src.data.get_common_data import BasicDataCache, load_common_data_from_db
from src.data.store_generation_data import store_generation_data_to_db

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

def get_and_store_generation_for_region(
        entsoe_client: EntsoePandasClient,
        sql_engine,
        region_code: str,
        start: pd.Timestamp,
        end: pd.Timestamp,
        cache: BasicDataCache,
        generation_type_filter: List[Tuple] = None) -> float | bool:
    """Retrieve electricity generation data via ENTSO-E REST interface for a given ENTSO-E region code
    and between two (panda-type) timestamps.
    Returns True if stores to database successfully. False otherwise

    @param sql_engine:
    @param region_code: ENTSO-E Region code
    @param start : Start pd.Timestamp
    @param end: End pd.Timestamp
    @param cache: EntsoeCache style object
    @param generation_type_filter: If passed, will only store the generation types listed in the database. Each element
        of the list should be a tuple, like ('Fossil Hard coal', 'Actual Aggregated')
    @return: bool. True if stores to database successfully. False otherwise
    """
    generation_type_to_id_mapping = cache.generation_type_mappings['ExternalName'].reset_index().set_index('ExternalName')['index'].to_dict()
    logging.info(f'Retrieving data for {region_code} for Date range FROM `{start}` TO `{end}` ...')
    s_0 = time.time()
    try:
        generation = entsoe_client.query_generation(region_code, start=start, end=end, psr_type=None)
    except NoMatchingDataError:
        logging.warning(f'NoMatchingDataError for {region_code} in date range')
        return False
    except requests.exceptions.HTTPError as e:
        logging.warning(f'HTTP error in entsoepy library. Skipping. Full error: {e}')
        return False
    e = time.time()
    logging.info(f'Retrieved in {e - s_0:.3f} s')

    generation_types_added = set()
    for generation_type_retrieved in generation.keys():
        generation_type_retrieved = generation_type_retrieved[0]
        if (generation_type_filter is not None) and (generation_type_retrieved not in generation_type_filter):
            logging.debug(
                f'Skipping generation type `{generation_type_retrieved}` as not in the generation type filter')
            continue

        # Map generation types to generationtypeid
        if generation_type_retrieved not in generation_type_to_id_mapping:
            logging.warning(f'No mapping for entsoepy generation type `{generation_type_retrieved}` to an internal generation type id. Will skip this generation type')
            continue
        generation_type_id = generation_type_to_id_mapping[generation_type_retrieved]

        # Map region to regionid
        region_index = (cache.regions['Code'] == region_code)
        if not region_index.any():
            raise ValueError(f'Could not find region {region_code} in the Regions table. Please run fill_regions()')
        region_id = cache.regions.loc[region_index, 'Id'].iloc[0]

        # Generation amounts in MW
        generation_data_to_add = generation[generation_type_retrieved]

        store_successful = store_generation_data_to_db(generation_data_to_add,
                                                       generation_type_id,
                                                       region_id,
                                                       sql_engine)
        if store_successful:
            generation_types_added.add(generation_type_retrieved)
    if generation_type_filter is not None:
        generation_types_in_filter_not_stored = set(generation_type_filter).difference(generation_types_added)
        if len(generation_types_in_filter_not_stored) > 0:
            logging.warning(
                f'Electricity data in region `{region_code}` was not stored for following generation types: {pprint.pformat(generation_types_in_filter_not_stored)}')
    return True


def main():
    dotenv.load_dotenv()
    ENTOSE_SECURITY_TOKEN = os.environ.get('ENTSOE_SECURITY_TOKEN')

    start = pd.Timestamp('20231202', tz='Europe/Brussels')
    end = pd.Timestamp('20231203', tz='Europe/Brussels')
    generation_type_filter = None # [('Fossil Hard coal', 'Actual Aggregated')]

    load_dotenv()
    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')
    PORT = os.getenv('ELEC_LCA_DB_PORT')

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
        get_and_store_generation_for_region(entsoe_client=client, sql_engine=sql_engine, region_code=region_code,start=start,end=end,cache=cache,generation_type_filter=generation_type_filter)
    e = time.time()
    logging.info(f'{e - s:.2f} s to retrieve and store data for {len(regions)} regions')


if __name__ == '__main__':
    main()
