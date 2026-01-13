"""
AI Service
Handles all AI-related operations using Gemini
"""

import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI operations"""

    def __init__(self):
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """Initialize Gemini LLM"""
        has_service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        has_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        try:
            if has_service_account and not has_api_key:
                from langchain_google_vertexai import ChatVertexAI
                self.llm = ChatVertexAI(
                    model_name="gemini-2.0-flash",
                    project=os.getenv("GOOGLE_PROJECT_ID"),
                    location="global",
                    temperature=0.7,
                    max_output_tokens=500
                )
                logger.info("✅ AI Service initialized with Vertex AI")
            elif has_api_key:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0.7,
                    max_output_tokens=500
                )
                logger.info("✅ AI Service initialized with Google AI")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI service: {e}")
            self.llm = None

    def generate_outlet_coaching(self, context: Dict[str, Any]) -> str:
        """
        Generate personalized coaching for outlet visit

        Args:
            context: Dictionary with outlet and DSR context

        Returns:
            Coaching message in Sinhala
        """
        if not self.llm:
            logger.error("LLM not initialized")
            return self._get_fallback_coaching()

        try:
            # Extract context
            dsr_name = context.get("dsr_name", "DSR")
            outlet_name = context.get("outlet_name", "")
            outlet_type = context.get("outlet_type", "")
            area = context.get("area", "")
            target = context.get("target", 0)
            last_visit = context.get("last_visit", 0)
            three_month_avg = context.get("three_month_avg", 0)
            top_skus = context.get("top_skus", [])
            poi_nearby = context.get("poi_nearby", [])
            monthly_completion = context.get("monthly_completion", 0)

            # Build SKU list
            sku_text = ", ".join([f"{sku['name']} ({sku['sales']:.0f}L)" for sku in top_skus])

            # Build POI list
            poi_text = ", ".join(poi_nearby) if poi_nearby else "විශේෂ POI නැත"

            # Determine performance status
            if last_visit >= target:
                performance = "හොඳ"
                performance_note = "පසුගිය visit එකේ target එක සපුරා ඇත"
            else:
                performance = "වැඩිදියුණු කළ හැකි"
                performance_note = f"target එකට වඩා {target - last_visit:.0f}L අඩුයි"

            # Build prompt
            prompt = f"""You are a supportive sales coach for a beverage DSR in Sri Lanka.

Generate coaching tips in Sinhala for {dsr_name} visiting {outlet_name} ({outlet_type}) in {area}.

Outlet Context:
- අද Target: {target:.0f}L
- පසුගිය visit: {last_visit:.0f}L ({performance_note})
- අවසන් මාස 3 සාමාන්‍යය: {three_month_avg:.0f}L
- මාසික සම්පූර්ණ කළ: {monthly_completion:.1f}%
- Performance: {performance}
- වඩාත්ම විකුණෙන භාණ්ඩ: {sku_text}
- ප්‍රදේශයේ POI: {poi_text}

Task:
Generate 3-4 SHORT, specific, actionable coaching tips in natural Sinhala.

Guidelines:
- Be encouraging and positive
- Reference the outlet's performance
- Suggest which products to focus on
- Use the location context (POI) to make relevant suggestions
- Keep each tip to 1-2 sentences max
- Use encouraging tone
- Format as bullet points (use •)
- AVOID technical jargon - use simple Sinhala
- If performance is good, congratulate and suggest how to maintain/improve
- If performance needs improvement, give constructive tips

Generate ONLY the tips in Sinhala, no other text or explanations."""

            # Call Gemini
            logger.info("   ├── Calling Gemini for outlet coaching...")
            response = self.llm.invoke(prompt)

            # Handle response
            if isinstance(response.content, list):
                parts = []
                for item in response.content:
                    if isinstance(item, dict):
                        parts.append(item.get('text', str(item)))
                    else:
                        parts.append(str(item))
                coaching = " ".join(parts).strip()
            elif isinstance(response.content, dict):
                coaching = response.content.get('text', str(response.content)).strip()
            else:
                coaching = str(response.content).strip()

            # Validate
            if not coaching or len(coaching) < 20:
                logger.warning("Generated coaching too short, using fallback")
                return self._get_fallback_coaching()

            logger.info(f"   └── Generated coaching: {len(coaching)} chars")
            return coaching

        except Exception as e:
            logger.error(f"Error generating coaching: {e}")
            return self._get_fallback_coaching()

    def _get_fallback_coaching(self) -> str:
        """Get fallback coaching message"""
        return """• පසුගිය visit එකේ performance බලලා අද වැඩිපුර විකුණන්න try කරන්න

• වඩාත්ම විකුණෙන භාණ්ඩ 2-3ක් promote කරන්න

• Customer handling skills use කරලා හොඳ relationship එකක් build කරන්න

• පොඩි offer එකක් දීලා sales වැඩි කරගන්න try කරන්න

ඔබට හැකියි! 💪"""


# Global instance
ai_service = AIService()
