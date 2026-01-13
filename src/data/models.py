"""
Data Models
Pydantic models for type safety and validation
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class Outlet(BaseModel):
    """Outlet model"""
    outlet_id: str
    outlet_name: str
    outlet_type: str
    area: str
    district: str
    latitude: float
    longitude: float
    poi_nearby: str
    cooler_available: str
    shelf_space_sqft: float

    @property
    def google_maps_link(self) -> str:
        """Generate Google Maps link"""
        return f"https://maps.google.com/?q={self.latitude},{self.longitude}"

    @property
    def poi_list(self) -> List[str]:
        """Get POI as list"""
        return self.poi_nearby.split("|") if self.poi_nearby else []


class DailyPlan(BaseModel):
    """Daily plan model"""
    dsr_name: str
    date: date
    outlet_id: str
    outlet_name: str
    outlet_type: str
    area: str
    priority: str
    target_sales_litres: float
    last_visit_sales_litres: float
    visit_order: int
    completed: str

    @property
    def is_priority(self) -> bool:
        """Check if priority outlet"""
        return self.priority.lower() == "yes"


class VisitHistory(BaseModel):
    """Visit history model"""
    dsr_name: str
    outlet_id: str
    visit_date: date
    sales_litres: float
    productive_visit: str


class SKUPerformance(BaseModel):
    """SKU performance model"""
    outlet_id: str
    sku_name: str
    avg_sales_per_visit_litres: float
    rank: int


class MonthlyTarget(BaseModel):
    """Monthly target model"""
    outlet_id: str
    year_month: str
    monthly_target_litres: float
    monthly_completed_litres: float

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.monthly_target_litres == 0:
            return 0
        return (self.monthly_completed_litres / self.monthly_target_litres) * 100


class OutletStatistics(BaseModel):
    """Outlet statistics aggregate"""
    outlet: Outlet
    daily_plan: DailyPlan
    monthly_target: MonthlyTarget
    top_skus: List[SKUPerformance]
    last_3_months_avg: float
    last_visit_sales: float
