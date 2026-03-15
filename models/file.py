from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    filename = Column(String)
    code_content = Column(String)