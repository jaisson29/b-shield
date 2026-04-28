from fastapi import HTTPException

from app.models.alert import AlertStatus
from app.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, alert_repository: AlertRepository):
        self.alert_repository = alert_repository

    def _now(self) -> str:
        from datetime import datetime

        return datetime.now().isoformat()

    def list_alerts(self, company_id: int | None, nivel=None, estado=None, desde=None):
        result = self.alert_repository.get_alerts_by_company_id_with_filters(
            company_id, nivel, estado, desde
        )
        return {
            "total": len(result),
            "filtros": {
                "company_id": company_id,
                "nivel": nivel,
                "estado": estado,
                "desde": desde,
            },
            "alerts": result,
        }

    def get_stats(self, company_id: int):
        alert_list = self.alert_repository.get_alerts_by_company_id(company_id)
        if not alert_list:
            raise HTTPException(
                404, detail="No se encontraron alertas para esta empresa"
            )
        by_level = {
            n: sum(1 for a in alert_list if a.critical_level == n)
            for n in ["critical", "high", "medium", "low"]
        }
        by_status = {
            e: sum(1 for a in alert_list if a.status == e)
            for e in ["pending", "reviewed", "mitigated", "ignored", "in_progress"]
        }

        critical_pending = sum(
            1
            for a in alert_list
            if a.critical_level == "critical" and a.status == "pending"
        )

        current_risk_level = "low"
        if critical_pending > 0:
            current_risk_level = "critical"
        elif by_level["high"] > 0:
            current_risk_level = "high"
        elif by_level["medium"] > 0:
            current_risk_level = "medium"

        return {
            "company_id": company_id,
            "total_alerts": len(alert_list),
            "by_level": by_level,
            "by_status": by_status,
            "active_critical_alerts": critical_pending,
            "current_risk_level": current_risk_level,
            "generated_at": self._now(),
        }

    def get_alert(self, alert_id):
        return self.alert_repository.get_alert_by_id(alert_id)

    def create_alert(self, alert_data):
        return self.alert_repository.create_alert(alert_data)

    def update_status(self, alert_id: int, status_data: str):
        status_data = status_data.lower()
        if status_data not in AlertStatus.__members__:
            raise HTTPException(400, detail="Estado no válido")
        status_data = AlertStatus[status_data]
        return self.alert_repository.update_status(alert_id, status_data)
