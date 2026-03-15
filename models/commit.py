from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    message = Column(String)
    author_id = Column(Integer)