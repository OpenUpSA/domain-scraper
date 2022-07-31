from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import sqlalchemy.sql.functions as func

Base = declarative_base()


class Scrape(Base):
    __tablename__ = 'scrape'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())
