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

    st.subheader('Data engineering concepts: We use Streamlit and VegaLite to visualize the data')

    region_code = st.selectbox(label='Region', options=cache.regions['Code'])

    st.text(region_code)

    start_date = st.date_input(label='Start date')
    st.text('Timezone: Europe (Brussels)')
    st.text(type(start_date))
    # TODO: Determine the timezone
    # Example chart from Streamlit documentation website, in order to arrange elementts
    hist_data = pd.DataFrame(np.random.normal(42, 10, (200, 1)), columns=["x"])

    @st.cache_data
    def altair_histogram():
        brushed = alt.selection_interval(encodings=["x"], name="brushed")

        return (
            alt.Chart(hist_data)
            .mark_bar()
            .encode(alt.X("x:Q", bin=True), y="count()")
            .add_params(brushed)
        )
    event_dict = altair_component(altair_chart=altair_histogram())

    r = event_dict.get("x")
    if r:
        filtered = hist_data[(hist_data.x >= r[0]) & (hist_data.x < r[1])]
        st.write(filtered)
    # TODO: Send calculation parameters
    if st.button('Calculate'):
        params = {
            'date_start': start_date,
            'region_code': 10
        }
        calculation_response = httpx.get('http://127.0.0.1:8000/calculate', params=params)
        if calculation_response.status_code >= 300 or calculation_response.status_code < 200:
            logging.warning(f'Calculation not successful. Status code: {calculation_response.status_code}')
        logging.debug(calculation_response.content, calculation_response.status_code)
        impact_df = pd.json_normalize(calculation_response.json())
        st.table(impact_df)

def get_available_dates(region_code):
    raise NotImplementedError()



if __name__ == '__main__':
    main()
