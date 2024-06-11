import sqlalchemy 
import os

db_type = os.environ.get('NER_DATABASE')
if  db_type and db_type == 'le':
    db_host = "localhost"
    db_user = "root"
    db_pass = ""
    db_name = "NER"
    db_port = 3306
else:
    db_host = "34.159.220.2"
    db_user = "SkSyGruppeE"
    db_pass = "cocacola"
    db_name = "SkSyProject"
    db_port = 3306

SQLALCHEMY_DATABASE_URI= sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name,
            )