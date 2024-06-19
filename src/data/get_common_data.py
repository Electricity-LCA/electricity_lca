import datetime
from dataclasses import dataclass

import pandas as pd
import sqlalchemy

from sqlalchemy.orm import sessionmaker


@dataclass
class BasicDataCache:
    generation_types: pd.DataFrame
    generation_type_mappings: pd.DataFrame
    regions: pd.DataFrame
    retrieved_timestamp: datetime.datetime


def load_common_data_from_db(sql_engine:sqlalchemy.engine.Engine):
    with sql_engine.connect() as conn:
        generation_types = pd.read_sql('SELECT * FROM public."ElectricityGenerationTypes"', conn.connection)
        generation_type_mappings = pd.read_sql('SELECT * FROM public."ElectricityGenerationTypesMapping"', conn.connection)
        regions = pd.read_sql('SELECT * FROM public."Regions"', conn.connection)
        retrieved_timestamp = datetime.datetime.now(datetime.timezone.utc)

        return BasicDataCache(generation_types=generation_types, regions=regions, retrieved_timestamp=retrieved_timestamp,generation_type_mappings=generation_type_mappings)
