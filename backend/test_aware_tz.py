import sys
from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import declarative_base, Session
import datetime

Base = declarative_base()

class AwareDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

class T(Base):
    __tablename__ = 't'
    id = Column(Integer, primary_key=True)
    d = Column(AwareDateTime)

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
s = Session(engine)

s.add(T(d=datetime.datetime.now(datetime.timezone.utc)))
s.commit()

obj = s.query(T).first()
print("Aware obj tzinfo:", obj.d.tzinfo)
