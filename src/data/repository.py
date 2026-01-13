"""
Data Repository
Clean data access layer for CSV files
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime
from .models import (
    Outlet, DailyPlan, VisitHistory,
    SKUPerformance, MonthlyTarget, OutletStatistics
)

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"


class DataRepository:
    """Repository for data access"""

    def __init__(self):
        self._daily_plan_df = None
        self._outlet_details_df = None
        self._visit_history_df = None
        self._sku_performance_df = None
        self._monthly_targets_df = None

    def _load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file with caching"""
        filepath = DATA_DIR / filename
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return pd.DataFrame()
        return pd.read_csv(filepath)

    @property
    def daily_plan_df(self) -> pd.DataFrame:
        """Lazy load daily plan"""
        if self._daily_plan_df is None:
            self._daily_plan_df = self._load_csv("daily_plan.csv")
            if not self._daily_plan_df.empty:
                self._daily_plan_df['date'] = pd.to_datetime(self._daily_plan_df['date'])
        return self._daily_plan_df

    @property
    def outlet_details_df(self) -> pd.DataFrame:
        """Lazy load outlet details"""
        if self._outlet_details_df is None:
            self._outlet_details_df = self._load_csv("outlet_details.csv")
        return self._outlet_details_df

    @property
    def visit_history_df(self) -> pd.DataFrame:
        """Lazy load visit history"""
        if self._visit_history_df is None:
            self._visit_history_df = self._load_csv("visit_history.csv")
            if not self._visit_history_df.empty:
                self._visit_history_df['visit_date'] = pd.to_datetime(self._visit_history_df['visit_date'])
        return self._visit_history_df

    @property
    def sku_performance_df(self) -> pd.DataFrame:
        """Lazy load SKU performance"""
        if self._sku_performance_df is None:
            self._sku_performance_df = self._load_csv("sku_performance_by_outlet.csv")
        return self._sku_performance_df

    @property
    def monthly_targets_df(self) -> pd.DataFrame:
        """Lazy load monthly targets"""
        if self._monthly_targets_df is None:
            self._monthly_targets_df = self._load_csv("outlet_monthly_targets.csv")
        return self._monthly_targets_df

    def get_daily_plan(self, dsr_name: str, target_date: date) -> List[DailyPlan]:
        """Get daily plan for DSR on specific date"""
        df = self.daily_plan_df
        if df.empty:
            return []

        filtered = df[
            (df['dsr_name'] == dsr_name) &
            (df['date'].dt.date == target_date)
        ]

        return [DailyPlan(**row.to_dict()) for _, row in filtered.iterrows()]

    def get_outlet_details(self, outlet_id: str) -> Optional[Outlet]:
        """Get outlet details by ID"""
        df = self.outlet_details_df
        if df.empty:
            return None

        filtered = df[df['outlet_id'] == outlet_id]
        if filtered.empty:
            return None

        return Outlet(**filtered.iloc[0].to_dict())

    def get_visit_history(self, outlet_id: str, limit: int = 10) -> List[VisitHistory]:
        """Get visit history for outlet"""
        df = self.visit_history_df
        if df.empty:
            return []

        filtered = df[df['outlet_id'] == outlet_id].sort_values('visit_date', ascending=False).head(limit)
        return [VisitHistory(**row.to_dict()) for _, row in filtered.iterrows()]

    def get_last_3_months_avg(self, dsr_name: str, outlet_id: str) -> float:
        """Calculate last 3 months average sales"""
        df = self.visit_history_df
        if df.empty:
            return 0.0

        three_months_ago = datetime.now() - pd.DateOffset(months=3)
        filtered = df[
            (df['dsr_name'] == dsr_name) &
            (df['outlet_id'] == outlet_id) &
            (df['visit_date'] >= three_months_ago)
        ]

        if filtered.empty:
            return 0.0

        return float(filtered['sales_litres'].mean())

    def get_top_skus(self, outlet_id: str, limit: int = 5) -> List[SKUPerformance]:
        """Get top SKUs for outlet"""
        df = self.sku_performance_df
        if df.empty:
            return []

        filtered = df[df['outlet_id'] == outlet_id].sort_values('rank').head(limit)
        return [SKUPerformance(**row.to_dict()) for _, row in filtered.iterrows()]

    def get_monthly_target(self, outlet_id: str, year_month: str) -> Optional[MonthlyTarget]:
        """Get monthly target for outlet"""
        df = self.monthly_targets_df
        if df.empty:
            return None

        filtered = df[
            (df['outlet_id'] == outlet_id) &
            (df['year_month'] == year_month)
        ]

        if filtered.empty:
            return None

        return MonthlyTarget(**filtered.iloc[0].to_dict())

    def get_outlet_statistics(self, dsr_name: str, outlet_id: str, target_date: date) -> Optional[OutletStatistics]:
        """Get complete outlet statistics"""
        # Get all required data
        daily_plans = self.get_daily_plan(dsr_name, target_date)
        if not daily_plans:
            return None

        daily_plan = next((p for p in daily_plans if p.outlet_id == outlet_id), None)
        if not daily_plan:
            return None

        outlet = self.get_outlet_details(outlet_id)
        if not outlet:
            return None

        # Get monthly target for current month
        year_month = target_date.strftime("%Y-%m")
        monthly_target = self.get_monthly_target(outlet_id, year_month)
        if not monthly_target:
            # Create default if not found
            monthly_target = MonthlyTarget(
                outlet_id=outlet_id,
                year_month=year_month,
                monthly_target_litres=0,
                monthly_completed_litres=0
            )

        # Get top SKUs
        top_skus = self.get_top_skus(outlet_id, limit=5)

        # Get 3-month average
        last_3_months_avg = self.get_last_3_months_avg(dsr_name, outlet_id)

        # Get last visit sales
        visit_history = self.get_visit_history(outlet_id, limit=1)
        last_visit_sales = visit_history[0].sales_litres if visit_history else 0.0

        return OutletStatistics(
            outlet=outlet,
            daily_plan=daily_plan,
            monthly_target=monthly_target,
            top_skus=top_skus,
            last_3_months_avg=last_3_months_avg,
            last_visit_sales=last_visit_sales
        )

    def get_area_wise_outlets(self, dsr_name: str, target_date: date) -> dict:
        """Get outlets grouped by area"""
        daily_plans = self.get_daily_plan(dsr_name, target_date)
        if not daily_plans:
            return {}

        # Group by area
        area_dict = {}
        for plan in daily_plans:
            if plan.area not in area_dict:
                area_dict[plan.area] = []
            area_dict[plan.area].append(plan)

        # Sort each area's outlets by visit_order
        for area in area_dict:
            area_dict[area] = sorted(area_dict[area], key=lambda x: x.visit_order)

        return area_dict


# Global repository instance
repository = DataRepository()
