from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.services.stats_service import StatsService


def dashboard(session: Session = Depends(get_session)):
    return StatsService(session).dashboard()


def monthly_report(session: Session = Depends(get_session)):
    return StatsService(session).monthly_report()
