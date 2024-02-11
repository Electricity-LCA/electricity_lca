# Multi-Impact Electricity modelling using live data sources
Estimate real-time environmental impacts using electricity generation data reported by national and super-national bodies

# Set up
1. Create an ENTSO-E account and request an API key
2. Decide on a place to run a database and [setup postgres](https://www.postgresql.org/docs/current/tutorial-install.html). 
3. Create an empty database called `electricity_lca` and create a user account with privilege to create tables on the database
4. Clone this repository
5. Copy `template_project.env` to a new file `.env` and fill the copied file with `ENTSOE_SECURITY_TOKEN` = your ENTSOE security token. Fill the connection details to your postgres sql instance
6. Create virtual environment
```commandline
venv create -r requirement.txt
```
7. Run `src/orm/create_database.py` to initalize the database schema and load static data 
8. Run all tests under `tests/`

# How to use
1. Run `launch.sh` (on linux)

# Data sources
## Environmental data
1. UNECE. _“Life Cycle Assessment of Electricity Generation Options | UNECE.”_ Accessed December 5, 2023. https://unece.org/sed/documents/2021/10/reports/life-cycle-assessment-electricity-generation-options.

##  Electricity data
1. ENTSO-E, for electricity generation data from European member states and electricity regions
2. Ember Global Monthly Data from https://ember-climate.org/data/data-catalogue/

See references for further

# Data Engineering Rational and Design Choice
## DevOps - GitHub and Pytest
- Repository code: https://github.com/tur-ium/electricity_lca (contact Artur for access)
- Standardization - cookiecutter data science template, `pandera` for ensuring conformance of data to expectations, table-level SQL constraints to perform validity checks
- Unit / integration testing : Pytest
- ETL - Python + pandas (with pyArrow)

## Database - Postgres
Data comes in tabular format => tabular relational database not Mongo / other document-oriented database

Reviewed common RDBMS’s : MySQL, SQLite, Microsoft SQL server, and Postgres. Decided for Postgres, based on the satisfaction of all project requirements
  - Free, open source, trustworthy and widely used
  - SQL standard conformity, functionality, and ease of use
  - Strong software ecosystem Support across cloud platforms, management tooling  (e.g. SQL Alchemy and pgAdmin)

Database schema and ORM managed using SQL Alchemy

Database initialized by running one python script -> create_database.py

## Cloud Platform - AWS
- Google Cloud Platform - Benefits: scale storage separate from db compute. Drawbacks: complex to connect to local dev env, limited trial, obscure pricing
- Saturn Cloud (https://saturncloud.io/) - only 10 free hours
- DeepNote - only support Jupyter Notebooks
- PythonAnywhere - benefits: ease-of-use, supports cron jobs, sharing shells, free tier. Drawbacks: not free to use postgres
- Amazon Web Services - 12 month free trial includes all required functionalities, good practical experience, scalable. Drawback - monopolized, vendor lock-in, limited trial

# Application structure
1. Pipelines for data retrieval from ENTSO-E can be found in the `src/data/` folder
2. ORM layer (src/orm) uses sqlalchemy `declarative_base` to provide an object-orientated interface for accessing and manipulating objects in the database. Also includes table creation in `create_database.py`
3. Calculation microservice (src/calculation/main.py:app)
4. Streamlit dashboard (src/visualization/main.py) shows the visual interface

The calculation microservice runs continuously in the background and receives requests from the dashboard when need to retrieve new data from the database or calculate fresh environmental impacts

# Acknowledgements
- This is a project undertaken as part of training for the _Data Engineering_ course run by [DataScientest](https://datascientest.com/) from August 2023 - July 2024. Concepts from the course have been applied where relevant to the project.
- The [data science cookiecutter template](https://github.com/drivendata/cookiecutter-data-science.git) by [DrivenData](https://www.drivendata.org/) for the starting structure for the project
- Last but not least my coach Gregor Wernet for the initial motivation for this project.