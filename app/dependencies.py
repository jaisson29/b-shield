from fastapi import Depends
from sqlalchemy.orm import Session


def get_db():
    from app.database import get_db

    return next(get_db())


def get_company_repository(db: Session = Depends(get_db)):
    from app.repositories.company_repository import CompanyRepository

    return CompanyRepository(db)


def get_alert_repository(db: Session = Depends(get_db)):
    from app.repositories.alert_repository import AlertRepository

    return AlertRepository(db)


def get_auth_service():
    from app.services.auth_service import AuthService

    return AuthService()


def get_alert_service(alert_repository=Depends(get_alert_repository)):
    from app.services.alerts_service import AlertService

    return AlertService(alert_repository=alert_repository)


def get_classification_service(
    company_repository=Depends(get_company_repository),
    alert_repository=Depends(get_alert_repository),
):
    from app.services.classifcation_service import ClassificationService

    return ClassificationService(
        company_repository=company_repository, alert_repository=alert_repository
    )


def get_company_service(company_repository=Depends(get_company_repository)):
    from app.services.companies_service import CompanyService

    return CompanyService(company_repository=company_repository)


def get_notification_service():
    from app.services.notification_service import NotificationService

    return NotificationService()


def get_ingestion_service(
    company_repository=Depends(get_company_repository),
    alert_repository=Depends(get_alert_repository),
    notification_service=Depends(get_notification_service),
    classification_service=Depends(get_classification_service),
):
    from app.services.ingestions_service import IngestionsService

    return IngestionsService(
        company_repository=company_repository,
        alert_repository=alert_repository,
        notification_service=notification_service,
        classification_service=classification_service,
    )
