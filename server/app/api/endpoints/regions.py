from fastapi import APIRouter, Query

from app.data.regions import get_provinces, get_cities, get_districts

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/provinces", response_model=list[str])
async def list_provinces():
    """返回全国省级行政区列表"""
    return get_provinces()


@router.get("/cities", response_model=list[str])
async def list_cities(province: str = Query(..., description="省/自治区/直辖市名称")):
    """根据省返回地级市列表"""
    return get_cities(province)


@router.get("/districts", response_model=list[str])
async def list_districts(
    province: str = Query(..., description="省/自治区/直辖市名称"),
    city: str = Query(..., description="地级市名称"),
):
    """根据省+市返回区县列表"""
    return get_districts(province, city)
