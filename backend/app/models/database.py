from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime,
    DECIMAL, Enum, ForeignKey, TIMESTAMP, text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from backend.app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_code = Column(String(50), unique=True, nullable=False)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    workshop = Column(String(50), nullable=False)
    production_line = Column(String(50), nullable=False)
    ideal_cycle_time = Column(DECIMAL(10, 2), nullable=False)
    status = Column(
        Enum("running", "idle", "maintenance", "breakdown"),
        default="idle",
    )
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    production_records = relationship("ProductionRecord", back_populates="equipment")
    downtime_records = relationship("DowntimeRecord", back_populates="equipment")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    product_category = Column(String(50))
    unit = Column(String(20), default="件")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    production_records = relationship("ProductionRecord", back_populates="product")


class ProductionPlan(Base):
    __tablename__ = "production_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_date = Column(Date, nullable=False)
    shift = Column(String(20), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    planned_quantity = Column(Integer, nullable=False)
    planned_duration_minutes = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ProductionRecord(Base):
    __tablename__ = "production_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_date = Column(Date, nullable=False)
    shift = Column(String(20), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    planned_duration_minutes = Column(Integer, nullable=False)
    actual_run_minutes = Column(DECIMAL(10, 2), nullable=False)
    total_count = Column(Integer, nullable=False)
    good_count = Column(Integer, nullable=False)
    defect_count = Column(Integer, nullable=False)
    ideal_cycle_time = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    equipment = relationship("Equipment", back_populates="production_records")
    product = relationship("Product", back_populates="production_records")


class DowntimeRecord(Base):
    __tablename__ = "downtime_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_date = Column(Date, nullable=False)
    shift = Column(String(20), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    downtime_type = Column(Enum("planned", "unplanned"), nullable=False)
    downtime_category = Column(String(50), nullable=False)
    downtime_reason = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    equipment = relationship("Equipment", back_populates="downtime_records")
