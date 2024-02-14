import pandas as pd


def load_unece_lcia_data() -> pd.DataFrame:
    df = pd.read_csv('/home/artur/PycharmProjects/electricity_lca/data/processed/lcia_elec_unece_table13.csv')
    return df
