from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Driver(Base):
    __tablename__ = "driver"

    driver_id = Column(String, primary_key=True)
    driver_number = Column(Integer)
    code = Column(String(3))
    given_name = Column(String)
    family_name = Column(String)
    birthday = Column(Date)
    nationality = Column(String)

    def fullname(self):
        return f'{self.given_name} {self.family_name}'

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
