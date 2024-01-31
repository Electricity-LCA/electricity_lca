from dotenv import load_dotenv
import os
from sqlalchemy.orm import declarative_base
import sqlalchemy as sqla

sql_alchemy_base = declarative_base()

class ImpactCategories(sql_alchemy_base):
    __tablename__ = 'ImpactCategories'
    Id = sqla.Column(sqla.Integer, primary_key=True)
    Name = sqla.Column(sqla.String(250), nullable=False)
    Unit = sqla.Column(sqla.String(50), nullable=False)


class ElectricityGenerationTypes(sql_alchemy_base):
    __tablename__ = 'ElectricityGenerationTypes'
    Id = sqla.Column(sqla.Integer,primary_key=True)
    Name = sqla.Column(sqla.String(50))

class EnvironmentalImpactsPerUnitEnergy(sql_alchemy_base):
    __tablename__ = 'EnvironmentalImpactsPerUnitEnergy'
    TypeId = sqla.Column(sqla.Integer,primary_key=True)
    SubTypeId = sqla.Column(sqla.Integer)
    ImpactCategoryId = sqla.Column(sqla.Integer)
    ImpactValue = sqla.Column(sqla.Float)
    ReferenceUnit = sqla.Column(sqla.String(20))
    ReferenceYear = sqla.Column(sqla.DateTime(), default=2021, nullable=False)
    __table_args__ = (
        sqla.ForeignKeyConstraint(['TypeId'], ['ElectricityGenerationTypes.Id']),
        sqla.ForeignKeyConstraint(['SubTypeId'], ['ElectricityGenerationTypes.Id']),
        sqla.ForeignKeyConstraint(['ImpactCategoryId'], ['ImpactCategories.Id']),
        sqla.UniqueConstraint('TypeId', 'SubTypeId', 'ImpactCategoryId', name='UX_EnvironmentalImpactsPerUnitEnergy',)
    )


class Regions(sql_alchemy_base):
    __tablename__ = 'Regions'
    Id = sqla.Column(sqla.Integer, primary_key=True)
    Code = sqla.Column(sqla.VARCHAR(36))
    Type = sqla.Column(sqla.VARCHAR(36)) # Currently `Country`
    Description = sqla.Column(sqla.VARCHAR(150))
class ElectricityGeneration(sql_alchemy_base):
    __tablename__ = 'ElectricityGeneration'
    Id = sqla.Column(sqla.Integer,primary_key=True)
    RegionId = sqla.Column(sqla.Integer)
    DateStamp = sqla.Column(sqla.DateTime)
    Biomass_Actual_Aggregated = sqla.Column(sqla.Float)
    Biomass_Actual_Consumption = sqla.Column(sqla.Float)
    Fossil_Gas_Actual_Aggregated = sqla.Column(sqla.Float)
    Fossil_Gas_Actual_Consumption = sqla.Column(sqla.Float)
    Fossil_Hard_coal_Actual_Aggregated = sqla.Column(sqla.Float)
    Fossil_Hard_coal_Actual_Consumption = sqla.Column(sqla.Float)
    Hydro_Run_of_river_and_poundage_Actual_Aggregated = sqla.Column(sqla.Float)
    Hydro_Run_of_river_and_poundage_Actual_Consumption = sqla.Column(sqla.Float)
    Nuclear_Actual_Aggregated = sqla.Column(sqla.Float)
    Nuclear_Actual_Consumption = sqla.Column(sqla.Float)
    Other_Actual_Aggregated = sqla.Column(sqla.Float)
    Other_Actual_Consumption = sqla.Column(sqla.Float)
    Solar_Actual_Aggregated = sqla.Column(sqla.Float)
    Solar_Actual_Consumption = sqla.Column(sqla.Float)
    Waste_Actual_Aggregated = sqla.Column(sqla.Float)
    Waste_Actual_Consumption = sqla.Column(sqla.Float)
    Wind_Offshore_Actual_Aggregated = sqla.Column(sqla.Float)
    Wind_Offshore_Actual_Consumption = sqla.Column(sqla.Float)
    Wind_Onshore_Actual_Aggregated = sqla.Column(sqla.Float)
    Wind_Onshore_Actual_Consumption = sqla.Column(sqla.Float)
    __table_args__ = (
        sqla.ForeignKeyConstraint(['RegionId'], ['Regions.Id']),
        sqla.UniqueConstraint('RegionId', 'DateStamp', name='UX_ElectricityGeneration', )
    )


def create_new_database(drop_existing=False):
    
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
    if drop_existing is True:
        sql_alchemy_base.metadata.drop_all(bind=engine)

    sql_alchemy_base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    create_new_database(drop_existing=False)