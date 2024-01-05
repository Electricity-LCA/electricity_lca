import os
import pandas as pd
import dotenv
from entsoe import EntsoePandasClient
from entsoe.mappings import Area
import time

def main():
    dotenv.load_dotenv()
    ENTOSE_SECURITY_TOKEN = os.environ.get('ENTSOE_SECURITY_TOKEN')
    
    countries = [x.name for x in Area]
    print(countries)
    client = EntsoePandasClient(api_key=ENTOSE_SECURITY_TOKEN)
    
    s= time.time()
    for country_code in countries:

        start = pd.Timestamp('20231201', tz='Europe/Brussels')
        end = pd.Timestamp('20231202', tz='Europe/Brussels')
        country_code = 'NL'  # Netherlands
        type_marketagreement_type = 'A01'
        contract_marketagreement_type = 'A01'
        process_type = 'A51'

        generation = client.query_generation(country_code, start=start, end=end, psr_type=None)
        print(generation)
    e=time.time()
    print(f'{e-s:.2f} s to load from all countries')
if __name__=='__main__':
    main()