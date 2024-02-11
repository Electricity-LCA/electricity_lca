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
        sqla.UniqueConstraint('TypeId', 'SubTypeId', 'ImpactCategoryId', name='UX_EnvironmentalImpactsPerUnitEnergy'),
    )


class Regions(sql_alchemy_base):
    __tablename__ = 'Regions'
    Id = sqla.Column(sqla.Integer, primary_key=True)
    Code = sqla.Column(sqla.VARCHAR(36))
    Type = sqla.Column(sqla.VARCHAR(36))  # Currently `Country`
    Description = sqla.Column(sqla.VARCHAR(150))
    __table_args__ = (
        sqla.UniqueConstraint('Code', name='UX_Regions'),
    )


class ElectricityGenerationNew(sql_alchemy_base):
    __tablename__ = 'ElectricityGenerationNew'
    Id = sqla.Column(sqla.Integer,primary_key=True)
    RegionId = sqla.Column(sqla.Integer)
    DateStamp = sqla.Column(sqla.DateTime)
    GenerationTypeId = sqla.Column(sqla.Integer)
    AggregatedGeneration = sqla.Column(sqla.Float)
    __table_args__ = (
        sqla.ForeignKeyConstraint(['RegionId'], ['Regions.Id']),
        sqla.ForeignKeyConstraint(['GenerationTypeId'], ['ElectricityGenerationTypes.Id']),
        sqla.UniqueConstraint('RegionId', 'DateStamp', name='UX_ElectricityGenerationNew'),
    )