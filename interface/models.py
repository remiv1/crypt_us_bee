from pymongo import MongoClient
from typing import Any
from os import getenv
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MongoDB setup
url_mongodb: str = getenv("MONGO_URI", "mongodb://mongodb:27017")
mongo_client: MongoClient[Any] = MongoClient(url_mongodb, tls=True, tlsAllowInvalidCertificates=True)
mongo_db = mongo_client[getenv("MONGO_INITDB_DATABASE", "my_database")]
mongo_collection = mongo_db[getenv("MONGO_COLLECTION_NAME", "beehive")]

# PostgreSQL setup
Base = declarative_base()
metadata = MetaData()
url_postgresql = f'postgresql://{getenv("POSTGRES_USER", "user")}:{getenv("POSTGRES_PASSWORD", "password")}@{getenv("POSTGRES_HOST", "localhost")}:{getenv("POSTGRES_PORT", "5432")}/{getenv("POSTGRES_DB", "my_database")}'
engine = create_engine(url_postgresql)
Session = sessionmaker(bind=engine)

# Define PostgreSQL table schema
class UsersGateway(Base):
    __tablename__ = getenv("POSTGRES_DB", "my_table")
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    pwd_hashed = Column(String, nullable=False)
    organisation_user_id = Column(String, nullable=True)    # foreignkey pour la table de l'organisation
    cryptkey = Column(String, nullable=False)               # clé de cryptage
    is_revoqued = Column(Boolean, default=False)            # statut de révocation

# Create the table in PostgreSQL
Base.metadata.create_all(engine)
