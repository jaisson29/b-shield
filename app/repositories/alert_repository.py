from datetime import datetime

from sqlalchemy.orm import Session

from app.models.alert import Alert


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, alert_data: Alert) -> Alert:
        self.db.add(alert_data)
        self.db.commit()
        self.db.refresh(alert_data)
        return alert_data
    
    def get_if_alert_exists(
        self, company_id: int, cwe_id: str, fecha_emision: datetime
    ) -> bool:
        return self.db.query(Alert).filter(
            Alert.company_id == company_id,
            Alert.cwe_id == cwe_id,
            Alert.emitted_at > fecha_emision
        ).first() is not None

    def get_alert_by_id(self, alert_id: int) -> Alert | None:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def get_alerts_by_company_id(self, company_id: int) -> list[Alert]:
        return self.db.query(Alert).filter(Alert.company_id == company_id).all()
