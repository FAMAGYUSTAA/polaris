from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, Session
import datetime
from sqlalchemy import text

Base = declarative_base()

class T1(Base):
    __tablename__ = 't1'
    id = Column(Integer, primary_key=True)
    d = Column(DateTime)

class T2(Base):
    __tablename__ = 't2'
    id = Column(Integer, primary_key=True)
    d = Column(DateTime(timezone=True))

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
s = Session(engine)

dt_aware = datetime.datetime.now(datetime.timezone.utc)
dt_naive = datetime.datetime.utcnow()

s.add(T1(d=dt_aware))
s.add(T2(d=dt_aware))
s.add(T1(d=dt_naive))
s.add(T2(d=dt_naive))
s.commit()

with engine.connect() as conn:
    print("T1 (DateTime) with aware:", conn.execute(text("SELECT d FROM t1 WHERE id=1")).fetchone())
    print("T2 (DateTime(timezone=True)) with aware:", conn.execute(text("SELECT d FROM t2 WHERE id=1")).fetchone())
    print("T1 (DateTime) with naive:", conn.execute(text("SELECT d FROM t1 WHERE id=2")).fetchone())
    print("T2 (DateTime(timezone=True)) with naive:", conn.execute(text("SELECT d FROM t2 WHERE id=2")).fetchone())

t1_obj = s.query(T1).filter_by(id=1).first()
t2_obj = s.query(T2).filter_by(id=1).first()
print("T1 obj tzinfo:", t1_obj.d.tzinfo)
print("T2 obj tzinfo:", t2_obj.d.tzinfo)
