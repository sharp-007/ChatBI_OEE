from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.app.services.nl2sql import nl2sql_service
from backend.app.services.oee_calculator import OEECalculator

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    success: bool
    sql: str = ""
    interpretation: str = ""
    chart_config: dict = {}
    data: dict = {}
    error: str = ""


@router.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """自然语言查询接口"""
    result = nl2sql_service.query(request.question)
    return ChatResponse(**result)


@router.get("/oee/overview")
async def oee_overview(
    start_date: str = Query(default="2026-01-01", description="开始日期"),
    end_date: str = Query(default="2026-03-31", description="结束日期"),
):
    """OEE概览数据"""
    return OEECalculator.get_overall_oee(start_date, end_date)


@router.get("/oee/trend")
async def oee_trend(
    start_date: str = Query(default="2026-01-01"),
    end_date: str = Query(default="2026-03-31"),
    group_by: str = Query(default="day", description="聚合维度: day/week/month"),
):
    """OEE趋势数据"""
    return OEECalculator.get_oee_trend(start_date, end_date, group_by)


@router.get("/oee/equipment-ranking")
async def equipment_ranking(
    start_date: str = Query(default="2026-01-01"),
    end_date: str = Query(default="2026-03-31"),
):
    """设备OEE排名"""
    return OEECalculator.get_equipment_ranking(start_date, end_date)


@router.get("/oee/workshop-summary")
async def workshop_summary(
    start_date: str = Query(default="2026-01-01"),
    end_date: str = Query(default="2026-03-31"),
):
    """车间OEE汇总"""
    return OEECalculator.get_workshop_summary(start_date, end_date)


@router.get("/oee/downtime-analysis")
async def downtime_analysis(
    start_date: str = Query(default="2026-01-01"),
    end_date: str = Query(default="2026-03-31"),
):
    """停机分析"""
    return OEECalculator.get_downtime_analysis(start_date, end_date)


@router.get("/oee/loss-analysis")
async def loss_analysis(
    start_date: str = Query(default="2026-01-01"),
    end_date: str = Query(default="2026-03-31"),
):
    """六大损失分析"""
    return OEECalculator.get_loss_analysis(start_date, end_date)
