"""
WARNING: This script clears any existing data in the following tables:
 - ElectricityGenerationTypes
 - ElectricityGenerationTypesMapping
 - EnvironmentalImpacts
 fills the database with
"""
import datetime
import logging
import os
import pandas as pd
import sqlalchemy as sqla
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from src.extract.unece_to_df import load_unece_lcia_data
from src.orm.base import ImpactCategories, ElectricityGenerationTypes

entsoe_generation_types_to_unece = {
    'Mixed': None,
    'Generation': None,
    'Load': None,
    'Biomass': None,
    'Fossil Brown coal/Lignite': 'Hard coal_PC without CCS',
    'Fossil Coal-derived gas': 'Natural gas_SC without CCS',
    'Fossil Gas': 'Natural gas_SC without CCS',
    'Fossil Hard coal': 'Hard coal_PC without CCS',
    'Fossil Oil': None,
    'Fossil Oil shale': None,
    'Fossil Peat': None,
    'Geothermal': None,
    'Hydro Pumped Storage': 'Hydro_360 MW',
    'Hydro Run-of-river and poundage': 'Hydro_360 MW',
    'Hydro Water Reservoir': 'Hydro_360 MW',
    'Marine': None,
    'Nuclear': 'Nuclear_average',
    'Other renewable': None,
    'Solar': 'PV_poly-Si ground-mounted',
    'Waste': None,
    'Wind Offshore': 'Wind_offshore concrete foundation',
    'Wind Onshore': 'Wind_onshore',
    'Other': None,
    'AC Link': None,
    'DC Link': None,
    'Substation': None,
    'Transformer': None}


def main():
    # Connect to database
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
    session_obj = sessionmaker(bind=engine)

    # Prepare generation types for saving to database
    unece_data = load_unece_lcia_data()

    # Transform
    unknown_generation_type_id = 0

    unece_data[['Type', 'Subtype']] = unece_data[['Type', 'Subtype']].apply(lambda x: x.str.strip())
    unece_data['GenerationTypeName'] = unece_data[['Type', 'Subtype']].agg('_'.join, axis=1)

    unece_generation_types = unece_data['GenerationTypeName'].drop_duplicates()
    unece_generation_types.loc[-1] = ['Unknown / not specified']

    unece_generation_types.index = unece_generation_types.index + 1  # Shift so that the unknown entry is 0 for ease of reading
    unece_generation_types = pd.DataFrame(unece_generation_types.rename('Name'))
    unece_generation_types.index.rename('Id', inplace=True)

    # Clear any existing ElectricityGenerationTypes from ElectricityGenerationTypes table
    with engine.connect() as connection:
        deletion_result = connection.execute(
            sqla.text(f'DELETE FROM public."ElectricityGenerationTypes"'))
        connection.commit()
    logging.info(f'{deletion_result.rowcount} rows deleted from ElectricityGenerationTypes')
    unece_generation_types.to_sql(name='ElectricityGenerationTypes', con=engine, if_exists='append', index=True)
    # upsert_successful = upsert_df(df=unece_generation_types,table_name='ElectricityGenerationTypes',engine=engine)

    # Check what we have in the database
    with session_obj() as session:
        query = (session.query(ElectricityGenerationTypes))
        internal_generation_types = pd.read_sql(query.statement, session.bind)
        assert len(internal_generation_types) == len(
            unece_generation_types)  # At the moment we only have unece generation type

    # Clear any electricity generation type mappings
    with engine.connect() as connection:
        deletion_result = connection.execute(
            sqla.text(f'DELETE FROM public."ElectricityGenerationTypesMapping"'))
        connection.commit()

    generation_mapping = pd.DataFrame.from_dict(entsoe_generation_types_to_unece, orient='index').reset_index().rename(
        {'index': 'ExternalName', 0: 'InternalName'}, axis=1)
    generation_mapping_2 = \
    generation_mapping.merge(internal_generation_types, left_on='InternalName', right_on='Name').rename(
        {'Id': 'ElectricityGenerationTypeId'}, axis=1)[['ExternalName', 'ElectricityGenerationTypeId']]
    generation_mapping_2.loc[:, 'ElectricityGenerationTypeId'] = generation_mapping_2.loc[:,
                                                                 'ElectricityGenerationTypeId'].fillna(
        unknown_generation_type_id)
    generation_mapping_2.loc[:, 'DataSourceName'] = 'UNECE'
    generation_mapping_2.loc[:,
    'Comment'] = f'Loaded from Table 13, UNECE. “Life Cycle Assessment of Electricity Generation Options | UNECE.” Accessed December 5, 2023. https://unece.org/sed/documents/2021/10/reports/life-cycle-assessment-electricity-generation-options.'
    generation_mapping_2.index.rename('Id', inplace=True)
    generation_mapping_2 = generation_mapping_2.reset_index()
    generation_mapping_2.to_sql(con=engine, name='ElectricityGenerationTypesMapping', if_exists='append', index=False)
    logging.info('done')

    # Transform data for loading into the ImpactCategories table
    impact_category_data_flattened = unece_data.drop(['Type', 'Subtype'], axis=1).melt(id_vars=['GenerationTypeName'],
                                                                                       var_name='ImpactCategoryName',
                                                                                       value_name='ImpactValue')
    impact_category_data_flattened['ImpactCategoryUnit'] = impact_category_data_flattened['ImpactCategoryName'].str.extract(
        r'\[(.{1,10})\]')
    impact_category_data_flattened['ImpactCategoryName'] = impact_category_data_flattened[
        'ImpactCategoryName'].str.extract(
        r'(.{1,500}) \[.{1,10}\]')

    impact_categories = impact_category_data_flattened[['ImpactCategoryName', 'ImpactCategoryUnit']]
    impact_categories.rename({'ImpactCategoryName': 'Name',
                              'ImpactCategoryUnit': 'Unit'},axis=1,inplace=True)
    impact_categories = impact_categories.drop_duplicates().reset_index().drop(['index'], axis=1)
    logging.info(f'There are {len(impact_categories)} impact categories to store')

    # Clear any existing impact categories from ImpactCategories table
    with engine.connect() as connection:
        deletion_result = connection.execute(
            sqla.text(f'DELETE FROM public."ImpactCategories"')
        )
        connection.commit()
        logging.info(f'{deletion_result.rowcount} rows deleted')

    impact_categories.to_sql(name='ImpactCategories', con=engine, if_exists='append', index=False)

    # Check what we have in the database
    with session_obj() as session:
        query = session.query(ImpactCategories)
        actual_impact_categories_df = pd.read_sql(query.statement, session.bind)
        assert len(actual_impact_categories_df) == len(
            impact_categories)  # At the moment we only have unece impact categories

    # Save the environmental categorization factors
    environmental_impacts_df = impact_category_data_flattened.merge(actual_impact_categories_df[['Id','Name']],
                                                                    left_on='ImpactCategoryName', right_on='Name')
    environmental_impacts_df.rename({'Id': 'ImpactCategoryId'}, axis=1, inplace=True)
    environmental_impacts_df.drop(['Name'], axis=1, inplace=True)
    environmental_impacts_df = environmental_impacts_df.merge(internal_generation_types[['Id','Name']], left_on='GenerationTypeName',
                                                              right_on='Name')
    environmental_impacts_df.rename({'Id': 'ElectricityGenerationTypeId'}, axis=1, inplace=True)
    environmental_impacts_df.drop(['Name'], axis=1, inplace=True)
    environmental_impacts_df['ReferenceYear'] = datetime.date(2021,1,1)
    environmental_impacts_df['PerUnit'] = 'kWh'
    environmental_impacts_df = environmental_impacts_df[
        ['ElectricityGenerationTypeId', 'ImpactCategoryId', 'ImpactValue', 'ImpactCategoryUnit', 'ReferenceYear']]
    environmental_impacts_df.drop_duplicates(['ElectricityGenerationTypeId', 'ImpactCategoryId'],inplace=True)
    environmental_impacts_df.to_sql(name='EnvironmentalImpacts', con=engine, if_exists='append', index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
