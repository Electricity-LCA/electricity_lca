import logging
import pandas as pd
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from src.microservice.constants import ServerError, ROW_LIMIT
from src.orm.base import Regions, ElectricityGeneration

NoDataStatusCode = 204


class GenerationResultSchema(BaseModel):
    GenerationUnit: str
    PerUnit: str
    ConversionFactor: float
    AggregatedGenerationConverted: float
    EnvironmentalImpact: float
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "result":
                    [{'Id': 7153, 'RegionId': 26, 'DateStamp': 1701475200000, 'GenerationTypeId': 2,
                      'AggregatedGeneration': 1398.0},
                     {'Id': 7154, 'RegionId': 26, 'DateStamp': 1701476100000, 'GenerationTypeId': 2,
                      'AggregatedGeneration': 1390.0},
                     {'Id': 7155, 'RegionId': 26, 'DateStamp': 1701477000000, 'GenerationTypeId': 2,
                      'AggregatedGeneration': 1390.0}]
            }]
        }
    }


async def get_earliest_date_for_region(region_code: str, engine):
    # TODO: Consider replacing with a lookup in the common data cached in the main body
    session_obj = sessionmaker(bind=engine)
    with session_obj() as session:
        region_id_query = session.query(Regions.Id).where(Regions.Code == region_code).limit(1)
        region_id_df = pd.read_sql(region_id_query.statement, session.bind)
        if region_id_df is None or region_id_df.shape[0] == 0:
            raise ValueError(f'Region Code `{region_code}` could not be found in database')
        elif region_id_df.shape[0] > 1:
            raise ServerError(
                f'More than one region found for region code `{region_code}`. There is probably an error in the database')

        region_id = int(region_id_df.iat[0, 0])

        query = (session.query(ElectricityGeneration.DateStamp)
                 .where(ElectricityGeneration.RegionId == region_id)
                 .order_by(ElectricityGeneration.DateStamp.asc())
                 .limit(1))
        earliest_record = pd.read_sql(query.statement, session.bind)
        if earliest_record.shape[0] == 0:
            return NoDataStatusCode
        else:
            return earliest_record.iat[0,0]


async def get_electricity_generation_df(date_start, date_end, region_code: str, generation_type_id: int,
                                        engine) -> pd.DataFrame:
    if not isinstance(region_code, str):
        raise TypeError('Invalid region code. Region code must be a string')

    if not isinstance(generation_type_id, int):
        raise TypeError('Invalid generation type id. Generation type id must be an integer')

    session_obj = sessionmaker(bind=engine)
    with session_obj() as session:
        impacts_query = session.query(Regions.Id).where(Regions.Code == region_code).limit(1)

        # TODO: Consider replacing with a lookup in the common data cached in the main body
        region_id_df = pd.read_sql(impacts_query.statement, session.bind)
        if region_id_df is None or region_id_df.shape[0] == 0:
            raise ValueError(f'Region Code `{region_code}` could not be found in database')
        elif region_id_df.shape[0] > 1:
            raise ServerError(
                f'More than one region found for region code `{region_code}`. There is probably an error in the database')

        region_id = int(region_id_df.iat[0, 0])
        logging.debug(f'REGION IS {region_id}')

        query = (session.query(ElectricityGeneration)
                 .where(ElectricityGeneration.GenerationTypeId == generation_type_id)
                 .where(ElectricityGeneration.RegionId == region_id)
                 .limit(ROW_LIMIT))

        df = pd.read_sql(query.statement, session.bind)
    return df