import datetime
import gzip
import logging
import os

import httpx
import sqlalchemy
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from pyarrow import feather
from streamlit_vega_lite import vega_lite_component, altair_component

from src.data.get_common_data import load_common_data_from_db


def main():
    logging.basicConfig(level=logging.DEBUG)
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

    cache = load_common_data_from_db(sql_engine=sql_engine)

    st.title('Electricity LCA Dashboard')

    region_code = st.selectbox(label='Region', options=cache.regions['Code'])
    st.text(region_code)

    generation_type_name = st.selectbox(label='Generation type', options=cache.generation_types['Name'])
    generation_type_id = 1

    start_date = st.date_input(label='Start date')
    st.text('Timezone: Europe (Brussels)')
    st.text(type(start_date))
    if st.button('Show electricity generation for period'):
        params = {
            'date_start': start_date,
            'region_code': region_code,
            'generation_type_id': generation_type_id
        }
        st.text(region_code)
        calculation_response = httpx.get('http://127.0.0.1:8000/generation', params=params)
        if calculation_response.status_code >= 300 or calculation_response.status_code < 200:
            logging.warning(f'Calculation not successful. Status code: {calculation_response.status_code}')
        impact_df = pd.DataFrame(calculation_response.json())
        impact_df['DateStamp'] = pd.to_datetime(impact_df['DateStamp'], utc=True,unit='ms')

        st.line_chart(impact_df, x='DateStamp', y='AggregatedGeneration', color='GenerationTypeId')
        with st.expander('See data'):
            st.table(impact_df)

def get_available_dates(region_code):
    raise NotImplementedError()



if __name__ == '__main__':
    main()
