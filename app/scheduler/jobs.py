from __future__ import annotations

import logging

from app.db.session import SessionLocal
from app.services.sla_service import check_ticket_sla_timeout as check_ticket_sla_timeout_service

logger = logging.getLogger(__name__)


def check_ticket_sla_timeout() -> None:
    """
    定时检查工单 SLA 是否超时。
    """
    logger.info("[SLA Job] start checking ticket SLA timeout")
    db = SessionLocal()
    try:
        result = check_ticket_sla_timeout_service(db)
        db.commit()
        logger.info(
            "[SLA Job] scanned=%s response_overdue=%s "
            "resolve_overdue=%s notification_created=%s skipped=%s",
            result.scanned,
            result.response_overdue,
            result.resolve_overdue,
            result.notification_created,
            result.skipped,
        )
    except Exception:
        db.rollback()
        logger.exception("[SLA Job] check ticket SLA timeout failed")
    finally:
        db.close()
        logger.info("[SLA Job] finished")
