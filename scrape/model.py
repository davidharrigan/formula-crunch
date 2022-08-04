from __future__ import annotations
from datetime import timedelta
from typing import List

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Interval, DateTime, Boolean
from sqlalchemy.orm import Session, declarative_base, relationship

Base = declarative_base()


class Driver(Base):
    __tablename__ = "driver"

    driver_id = Column(String, primary_key=True)
    permanent_number = Column(Integer)
    code = Column(String(3))
    first_name = Column(String)
    last_name = Column(String)
    birthday = Column(Date)
    nationality = Column(String)

    def fullname(self):
        return f"{self.given_name} {self.family_name}"

    def __repr__(self):
        return f"Driver(driver_id={self.driver_id!r}, driver_number={self.driver_number!r}, code={self.code!r})"


class Circuit(Base):
    __tablename__ = "circuit"

    circuit_id = Column(String, primary_key=True)
    name = Column(String)
    locality = Column(String)
    country = Column(String)


class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    date = Column(Date)
    event_name = Column(String)
    round_number = Column(Integer)
    drivers = Column(Integer)
    circuit_id = Column(String, ForeignKey("circuit.circuit_id"))

    def __repr__(self):
        return f"Race(id={self.id!r}, year={self.year!r}, date={self.date!r}, round_number={self.round_number!r})"

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> Race:
        race = (
            session.query(cls)
            .filter_by(date=kwargs["date"], round_number=kwargs["round_number"])
            .one_or_none()
        )
        if race:
            return race
        race = cls(**kwargs)
        session.add(race)
        return race


class DriverRaceSummary(Base):
    __tablename__ = "driver_race_summary"

    id = Column(Integer, primary_key=True)

    grid_position = Column(String)
    position = Column(String)
    points = Column(Integer)
    season_standing = Column(Integer)
    season_points = Column(Integer)
    status = Column(String)

    wins = Column(Integer, default=0)
    podiums = Column(Integer, default=0)
    laps_completed = Column(Integer)

    qa_done = Column(Boolean)

    driver_id = Column(String, ForeignKey("driver.driver_id"))
    race_id = Column(Integer, ForeignKey("race.id"))

    driver: Driver = relationship("Driver")
    race: Race = relationship("Race")

    lap_summary: LapSummary = relationship("LapSummary")
    pit_stop_summary: PitSummary = relationship("PitSummary")
    overtakes: List[Overtake] = relationship("Overtake")

    def __repr__(self):
        return f"DriverRaceSummary(id={self.id!r}, driver_id={self.driver_id!r}, race_id={self.race_id!r})"

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> DriverRaceSummary:
        rs = (
            session.query(cls)
            .filter_by(race_id=kwargs["race_id"], driver_id=kwargs["driver_id"])
            .one_or_none()
        )
        if rs:
            return rs
        rs = cls(**kwargs)
        session.add(rs)
        return rs

    @classmethod
    def upsert(cls, session: Session, **kwargs) -> DriverRaceSummary:
        rs = (
            session.query(cls)
            .filter_by(race_id=kwargs["race_id"], driver_id=kwargs["driver_id"])
            .one_or_none()
        )
        if rs:
            for k, v in kwargs.items():
                setattr(rs, k, v)
            return rs
        else:
            rs = cls(**kwargs)
            session.add(rs)
            return rs


class LapSummary(Base):
    __tablename__ = "lap_summary"

    id = Column(Integer, primary_key=True)
    driver_race_summary_id = Column(Integer, ForeignKey("driver_race_summary.id"))

    fastest_lap = Column(Integer)
    fastest_lap_time = Column(Interval)
    fastest_lap_average_speed = Column(Float)
    fastest_lap_speed_trap = Column(Float)
    average_time = Column(Interval)
    average_speed = Column(Float)
    fastest_speed_trap = Column(Float)

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> LapSummary:
        ls = (
            session.query(cls)
            .filter_by(driver_race_summary_id=kwargs["driver_race_summary_id"])
            .one_or_none()
        )
        if ls:
            return ls
        ls = cls(**kwargs)
        session.add(ls)
        return ls


class PitSummary(Base):
    __tablename__ = "pit_summary"

    id = Column(Integer, primary_key=True)
    driver_race_summary_id = Column(Integer, ForeignKey("driver_race_summary.id"))

    average: timedelta = Column(Interval)
    total_time: timedelta = Column(Interval)
    pit_stops: List[PitStop] = relationship("PitStop")

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> PitSummary:
        ps = (
            session.query(cls)
            .filter_by(driver_race_summary_id=kwargs["driver_race_summary_id"])
            .one_or_none()
        )
        if ps:
            return ps
        ps = cls(**kwargs)
        session.add(ps)
        return ps


class PitStop(Base):
    __tablename__ = "pit_stop"

    id = Column(Integer, primary_key=True)
    pit_summary_id = Column(Integer, ForeignKey("pit_summary.id"))

    lap_number = Column(Integer)
    stop = Column(Integer)
    duration = Column(Interval)

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> PitStop:
        ps = (
            session.query(cls)
            .filter_by(pit_summary_id=kwargs["pit_summary_id"], lap_number=kwargs["lap_number"])
            .one_or_none()
        )
        if ps:
            return ps
        ps = cls(**kwargs)
        session.add(ps)
        return ps


class Overtake(Base):
    __tablename__ = "overtake"

    id = Column(Integer, primary_key=True)
    driver_race_summary_id = Column(Integer, ForeignKey("driver_race_summary.id"))

    time = Column(Interval)
    lap_number = Column(Integer)
    position = Column(Integer)
    passed_driver_id = Column(String, ForeignKey("driver.driver_id"))
    passing_status = Column(String)
    passing_status_override = Column(String)
    passing_status_override_reason = Column(String)

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> PitStop:
        ps = (
            session.query(cls)
            .filter_by(
                driver_race_summary_id=kwargs["driver_race_summary_id"],
                time=kwargs["time"],
                lap_number=kwargs["lap_number"],
                position=kwargs["position"],
                passed_driver_id=kwargs["passed_driver_id"],
                passing_status=kwargs["passing_status"],
            )
            .one_or_none()
        )
        if ps:
            return ps
        ps = cls(**kwargs)
        session.add(ps)
        return ps
