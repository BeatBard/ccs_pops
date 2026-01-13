"""
Intent Classifier
Uses Gemini AI to classify user intents from natural language
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv
from ..core.constants import Intent, GREETING_KEYWORDS

load_dotenv()

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user messages to intents using Gemini"""

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
                    temperature=0.3,  # Lower temperature for consistent classification
                    max_output_tokens=50
                )
                logger.info("✅ Intent classifier initialized with Vertex AI")
            elif has_api_key:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0.3,
                    max_output_tokens=50
                )
                logger.info("✅ Intent classifier initialized with Google AI")
        except Exception as e:
            logger.error(f"❌ Failed to initialize intent classifier: {e}")
            self.llm = None

    def classify(self, message: str, current_state: str) -> Intent:
        """
        Classify user message to intent

        Args:
            message: User message text
            current_state: Current conversation state

        Returns:
            Intent enum
        """
        message_lower = message.lower().strip()

        # Rule-based classification for common patterns
        # 1. Greetings
        if any(keyword in message_lower for keyword in GREETING_KEYWORDS):
            logger.info(f"📌 Intent: GREETING (rule-based)")
            return Intent.GREETING

        # 2. Numbers (for outlet selection)
        if message_lower.isdigit():
            logger.info(f"📌 Intent: OUTLET_NUMBER (rule-based)")
            return Intent.OUTLET_NUMBER

        # 3. Button actions (already handled by routing, but keep as fallback)
        if any(keyword in message_lower for keyword in ["check-in", "checkin", "සැලැස්ම"]):
            logger.info(f"📌 Intent: CHECKIN (rule-based)")
            return Intent.CHECKIN

        if any(keyword in message_lower for keyword in ["outlet", "විස්තර"]):
            logger.info(f"📌 Intent: OUTLET_DETAILS (rule-based)")
            return Intent.OUTLET_DETAILS

        if any(keyword in message_lower for keyword in ["end", "අවසානය", "summary"]):
            logger.info(f"📌 Intent: END_SUMMARY (rule-based)")
            return Intent.END_SUMMARY

        if any(keyword in message_lower for keyword in ["area", "ප්‍රදේශ"]):
            logger.info(f"📌 Intent: AREA_VIEW (rule-based)")
            return Intent.AREA_VIEW

        # 4. Use AI for complex/ambiguous messages
        if self.llm:
            try:
                ai_intent = self._classify_with_ai(message, current_state)
                if ai_intent:
                    logger.info(f"📌 Intent: {ai_intent} (AI-based)")
                    return ai_intent
            except Exception as e:
                logger.error(f"AI classification failed: {e}")

        # 5. Default to UNKNOWN
        logger.info(f"📌 Intent: UNKNOWN (no match)")
        return Intent.UNKNOWN

    def _classify_with_ai(self, message: str, current_state: str) -> Optional[Intent]:
        """Use Gemini AI to classify intent"""
        if not self.llm:
            return None

        prompt = f"""You are an intent classifier for a sales assistant chatbot in Sinhala/English.

Current State: {current_state}
User Message: "{message}"

Classify the user's intent into ONE of these categories:
- greeting: User is greeting (හායි, හෙලෝ, hi, hello, good morning)
- checkin: User wants to check-in or see today's plan (සැලැස්ම, plan, check-in)
- outlet_details: User wants outlet information (outlet, විස්තර, details)
- area_view: User wants to see outlets by area (ප්‍රදේශ, area)
- end_summary: User wants end of day summary (අවසානය, summary, end of day)
- outlet_number: User provided a number (1, 2, 3, etc.)
- unknown: Cannot determine intent

Reply with ONLY the category name, nothing else."""

        try:
            response = self.llm.invoke(prompt)
            intent_str = str(response.content).strip().lower()

            # Map response to Intent enum
            intent_mapping = {
                "greeting": Intent.GREETING,
                "checkin": Intent.CHECKIN,
                "outlet_details": Intent.OUTLET_DETAILS,
                "area_view": Intent.AREA_VIEW,
                "end_summary": Intent.END_SUMMARY,
                "outlet_number": Intent.OUTLET_NUMBER,
                "unknown": Intent.UNKNOWN,
            }

            return intent_mapping.get(intent_str, Intent.UNKNOWN)

        except Exception as e:
            logger.error(f"Error in AI classification: {e}")
            return None


# Global intent classifier instance
intent_classifier = IntentClassifier()
