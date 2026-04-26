"""
B-Shield Alert System — Servicio: Notificaciones
Implementa el RF-05: notificar alertas Críticas y Altas.

Canales disponibles:
  - Consola estructurada (activo siempre — para logs)
  - Email SMTP      (activo si EMAIL_HOST está en .env)
  - Slack webhook   (activo si SLACK_WEBHOOK_URL está en .env)

Para agregar un canal nuevo: agregar una función _notify_<canal>
y llamarla al final de notify_alert().
"""

import os
import json
from datetime import datetime, timezone

from app.models.alert import Alert
from app.models.company import Company


class NotificationService:
    # ── Colores para la consola ───────────────────────────────────
    _COLORS = {
        "Critico": "\033[91m",  # Rojo
        "Alto": "\033[33m",  # Amarillo
        "Medio": "\033[94m",  # Azul claro
        "Bajo": "\033[92m",  # Verde
        "RESET": "\033[0m",
    }

    def _notify_console(self, alerta: Alert, empresa: Company) -> None:
        """Canal 1: log estructurado en consola (siempre activo)."""
        nivel = alerta.critical_level
        color = self._COLORS.get(nivel, "")
        reset = self._COLORS["RESET"]
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"\n{color}{'═'*60}")
        print(f"  🚨 ALERTA {nivel.upper()} — B-Shield Notification")
        print(f"{'═'*60}{reset}")
        print(f"  Empresa   : {empresa.name} ({alerta.company_id})")
        print(f"  CWE       : {alerta.cwe_id} — {alerta.cwe_name}")
        print(f"  CVSS      : {alerta.cvss_score}  |  IRC: {alerta.irc_score}")
        print(f"  Afecta    : {', '.join(alerta.affected_technologies)}")
        print(f"  Descripción: {alerta.description[:80]}...")
        print(f"  Mitigación : {alerta.recommendation[:80]}...")
        print(f"  Fuente    : {alerta.source_url}")
        print(f"  Timestamp : {ts}")
        print(f"  Alerta ID : {alerta.id}")
        print(f"{color}{'═'*60}{reset}\n")

    def _notify_slack(self, alerta: Alert, empresa: Company) -> None:
        """
        Canal 2: Slack via Incoming Webhook.
        Activo cuando SLACK_WEBHOOK_URL está definido en el entorno.

        Para activar:
          export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
        """
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return

        try:
            import urllib.request

            nivel = alerta.critical_level
            emoji = {"Critico": "🚨", "Alto": "⚠️", "Medio": "🔔", "Bajo": "✅"}.get(
                nivel, "🔔"
            )
            color = {
                "Critico": "danger",
                "Alto": "warning",
                "Medio": "#4A90E2",
                "Bajo": "good",
            }.get(nivel, "good")

            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"{emoji} Alerta {nivel}: {alerta.cwe_id} — {alerta.cwe_name}",
                        "fields": [
                            {"title": "Empresa", "value": empresa.name, "short": True},
                            {
                                "title": "CVSS / IRC",
                                "value": f"{alerta.cvss_score} / {alerta.irc_score}",
                                "short": True,
                            },
                            {
                                "title": "Tecnologías",
                                "value": ", ".join(alerta.affected_technologies),
                                "short": False,
                            },
                            {
                                "title": "Mitigación",
                                "value": alerta.recommendation,
                                "short": False,
                            },
                        ],
                        "footer": f"B-Shield Alert System | {alerta.id}",
                    }
                ]
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url, data=data, headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=5)
            print(f"[Notif] Slack enviado para alerta {alerta.id}")

        except Exception as e:
            print(f"[Notif][ERROR] Fallo al enviar a Slack: {e}")

    def _notify_email(self, alerta: Alert, empresa: Company) -> None:
        """
        Canal 3: Email SMTP.
        Activo cuando EMAIL_HOST, EMAIL_USER y EMAIL_PASSWORD están en el entorno.

        Para activar:
          export EMAIL_HOST=smtp.gmail.com
          export EMAIL_PORT=587
          export EMAIL_USER=tu@correo.com
          export EMAIL_PASSWORD=tu_password
        """
        host = os.getenv("EMAIL_HOST")
        user = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        port = int(os.getenv("EMAIL_PORT", "587"))
        dest = empresa.email

        assert host is not None, "EMAIL_HOST no configurado"
        assert user is not None, "EMAIL_USER no configurado"
        assert password is not None, "EMAIL_PASSWORD no configurado"
        assert dest is not None, "Empresa sin contacto_email"

        if not all([host, user, password, dest]):
            return  # Canal no configurado o empresa sin email

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            nivel = alerta.critical_level
            emoji = {"Critico": "🚨", "Alto": "⚠️", "Medio": "🔔", "Bajo": "✅"}.get(
                nivel, "🔔"
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"{emoji} B-Shield: Alerta {nivel} — {alerta.cwe_id}"
            msg["From"] = user
            msg["To"] = dest

            html = f"""
            <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
              <div style="background:#1A3E6F;padding:20px;border-radius:8px 8px 0 0;">
                <h2 style="color:#fff;margin:0;">🛡 B-Shield Alert System</h2>
                <p style="color:#94a3b8;margin:4px 0 0;">Sistema de Inteligencia Preventiva de Seguridad</p>
              </div>
              <div style="background:#fff;border:1px solid #e2e8f0;border-radius:0 0 8px 8px;padding:24px;">
                <h3 style="color:#dc2626;">{emoji} Alerta {nivel}: {alerta.cwe_id}</h3>
                <p><strong>Empresa:</strong> {empresa.name}</p>
                <p><strong>Vulnerabilidad:</strong> {alerta.cwe_name}</p>
                <p><strong>CVSS:</strong> {alerta.cvss_score} | <strong>IRC:</strong> {alerta.irc_score}</p>
                <p><strong>Tecnologías afectadas:</strong> {', '.join(alerta.affected_technologies)}</p>
                <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:6px;padding:12px;margin:16px 0;">
                  <strong>💡 Mitigación:</strong><br>{alerta.recommendation}
                </div>
                <p><strong>Descripción:</strong> {alerta.description}</p>
                <p><a href="{alerta.source_url}">Ver reporte en HackerOne</a></p>
                <hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0;">
                <p style="color:#94a3b8;font-size:12px;">Alerta ID: {alerta.id} | B-Shield v1.0</p>
              </div>
            </body></html>
            """

            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(user, dest, msg.as_string())

            print(f"[Notif] Email enviado a {dest} para alerta {alerta.id}")

        except Exception as e:
            print(f"[Notif][ERROR] Fallo al enviar email: {e}")

    # ── Punto de entrada principal ────────────────────────────────

    def notify_alert(self, alerta: Alert, empresa: Company) -> None:
        """
        Dispara todos los canales de notificación configurados.
        Siempre ejecuta la consola; los demás dependen del entorno.
        """
        self._notify_console(alerta, empresa)
        self._notify_slack(alerta, empresa)
        self._notify_email(alerta, empresa)
