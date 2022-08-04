from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import sqlalchemy.sql.functions as func

Base = declarative_base()


class Scrape(Base):
    __tablename__ = "scrape"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    page_observations = relationship("PageObservation", back_populates="scrape")
    file_observations = relationship("FileObservation", back_populates="scrape")


class Page(Base):
    """
    The content of a page
    """

    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    observations = relationship("PageObservation", back_populates="page")
    html = Column(String, nullable=False)
    sha256 = Column(String, nullable=False, unique=True)


class PageObservation(Base):
    """
    An observation of a given page
    """

    __tablename__ = "page_observation"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    scrape_id = Column(Integer, ForeignKey("scrape.id"))
    scrape = relationship("Scrape", back_populates="page_observations")
    page_id = Column(Integer, ForeignKey("page.id"))
    page = relationship("Page", back_populates="observations")
    url = Column(String, nullable=False)
    referrer = Column(String, nullable=False)
    etag = Column(String, nullable=True)


class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    observations = relationship("FileObservation", back_populates="file")
    content_type = Column(String, nullable=False)
    sha256 = Column(String, nullable=False, unique=True)
    content_disposition_filename = Column(String, nullable=False)

class FileObservation(Base):
    __tablename__ = "file_observation"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    scrape_id = Column(Integer, ForeignKey("scrape.id"))
    scrape = relationship("Scrape", back_populates="file_observations")
    file_id = Column(Integer, ForeignKey("file.id"))
    file = relationship("File", back_populates="observations")
    url = Column(String, nullable=False)
    referrer = Column(String, nullable=True)
    etag = Column(String, nullable=True)
