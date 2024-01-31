# electricity_lca
Convert live electricity data streams into LCA models

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

# Running
TBD

# Datasets
## Environmental data
1. UNECE. _“Life Cycle Assessment of Electricity Generation Options | UNECE.”_ Accessed December 5, 2023. https://unece.org/sed/documents/2021/10/reports/life-cycle-assessment-electricity-generation-options.

##  Electricity data
1. ENTSO-E
2. Ember Global Monthly Data from https://ember-climate.org/data/data-catalogue/

   


# Acknowledgements
This project is structured based on [data science cookiecutter template](https://github.com/drivendata/cookiecutter-data-science.git) by [DrivenData](https://www.drivendata.org/) 
