import os
import pandas as pd
import dotenv
from entsoe import EntsoePandasClient

def main():
    dotenv.load_dotenv()
    ENTOSE_SECURITY_TOKEN = os.environ.get('ENTSOE_SECURITY_TOKEN')
    
    client = EntsoePandasClient(api_key=ENTOSE_SECURITY_TOKEN)
    
    start = pd.Timestamp('20231201', tz='Europe/Brussels')
    end = pd.Timestamp('20231202', tz='Europe/Brussels')
    country_code = 'NL'  # Netherlands
    type_marketagreement_type = 'A01'
    contract_marketagreement_type = 'A01'
    process_type = 'A51'
    
    generation = client.query_generation(country_code, start=start, end=end, psr_type=None)
    print(generation)
    
if __name__=='__main__':
    main()