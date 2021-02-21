import glob
import os
import sqlalchemy

def clean_up_database(database_file_path):
    if len(glob.glob(database_file_path)) > 0:
        os.remove(database_file_path)

def create_new_sqlite_file(database_file_path):
    engine = sqlalchemy.create_engine(database_file_path)
    metadata = sqlalchemy.MetaData()

    results = sqlalchemy.Table(
        'results',
        metadata,
        sqlalchemy.Column(
            'id',
            sqlalchemy.Integer(),
            primary_key=True
        ),
        sqlalchemy.Column(
            'url',
            sqlalchemy.String(2048),
            nullable=False
        ),
        sqlalchemy.Column(
            'last_crawl_timestamp',
            sqlalchemy.DateTime()
        ),
        sqlalchemy.Column(
            'last_crawl_status_code',
            sqlalchemy.Integer(),
            nullable=False
        )
    )

    metadata.create_all(engine) #Create the table

def main():
    database_file_path = 'sqlite:///db/seaspider.sqlite'
    clean_up_database(database_file_path)
    create_new_sqlite_file(database_file_path)

main()
