from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import require_permissions
from app.core.responses import success
from app.models import User

router = APIRouter()


@router.get("")
def dicts(_: Annotated[User, Depends(require_permissions("dict:view"))]) -> dict:
    return success(
        {
            "roles": [
                {"label": "管理员", "value": "admin"},
                {"label": "IT运维人员", "value": "it_staff"},
                {"label": "普通员工", "value": "employee"},
            ],
            "ticket_status": [
                {"label": "待受理", "value": "pending_accept"},
                {"label": "待派单", "value": "pending"},
                {"label": "已分配", "value": "assigned"},
                {"label": "处理中", "value": "processing"},
                {"label": "待用户确认", "value": "pending_confirm"},
                {"label": "已完成", "value": "completed"},
                {"label": "已关闭", "value": "closed"},
                {"label": "已取消", "value": "cancelled"},
            ],
            "ticket_priority": [
                {"label": "低", "value": "low"},
                {"label": "普通", "value": "normal"},
                {"label": "高", "value": "high"},
                {"label": "紧急", "value": "urgent"},
            ],
            "asset_status": [
                {"label": "在用", "value": "in_use"},
                {"label": "闲置", "value": "idle"},
                {"label": "维修中", "value": "repairing"},
                {"label": "已报废", "value": "scrapped"},
            ],
            "faq_category": [
                {"label": "电脑问题", "value": "computer"},
                {"label": "网络问题", "value": "network"},
                {"label": "打印机问题", "value": "printer"},
                {"label": "账号系统问题", "value": "account"},
                {"label": "其他问题", "value": "other"},
            ],
        }
    )
