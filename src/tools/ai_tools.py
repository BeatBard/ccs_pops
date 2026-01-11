"""
AI Coaching Tools
Tools that use Gemini AI for generating personalized coaching
"""

from langchain.tools import tool
from typing import Dict, Any
import logging
import os
import warnings

# Suppress deprecation warning for ChatVertexAI
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_google_vertexai")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize Gemini model
llm = None

def init_gemini():
    """Initialize Gemini model based on available credentials"""
    global llm
    
    # Check if using Vertex AI (service account) or Google AI (API key)
    has_service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    has_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if has_service_account and not has_api_key:
        # Use Vertex AI with service account
        try:
            from langchain_google_vertexai import ChatVertexAI
            llm = ChatVertexAI(
                model_name="gemini-2.0-flash",
                project=os.getenv("GOOGLE_PROJECT_ID", "amiable-catfish-433412-d9"),
                location="global",
                temperature=0.7,
                max_output_tokens=500
            )
            logger.info("Initialized Gemini using Vertex AI (service account)")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
    
    elif has_api_key:
        # Use Google AI with API key
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.7,
                max_output_tokens=500
            )
            logger.info("Initialized Gemini using Google AI (API key)")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize Google AI: {e}")
    
    else:
        logger.error("No Google credentials found. Set GOOGLE_APPLICATION_CREDENTIALS for Vertex AI or GOOGLE_API_KEY for Google AI")
    
    return None

# Initialize on module load
llm = init_gemini()


@tool
def generate_ai_coaching_tool(context: Dict[str, Any]) -> str:
    """Generate AI-powered coaching using Gemini based on DSR and outlet context.

    Args:
        context: Dictionary with DSR profile, outlet info, LIPB data, SKU info, etc.
            Expected keys:
            - dsr_name: Name of DSR
            - strengths: List of DSR strengths
            - dev_areas: List of development areas
            - outlet_type: Type of outlet (SMMT, Eatery, etc.)
            - outlet_name: Name of outlet
            - lipb: Current LIPB
            - target_lipb: Target LIPB
            - issues: List of issues (e.g., ["visibility", "low stock"])
            - top_skus: List of top SKUs
            - rule_tips: Any rule-based tips to incorporate

    Returns:
        Coaching message in Sinhala (or English if Sinhala generation fails)
    """
    logger.info("🤖 AI COACHING TOOL INVOKED")
    
    if not llm:
        logger.error("❌ LLM not initialized!")
        return "දෝෂයක්: AI coaching සේවාව දැනට ලබා ගත නොහැක"

    try:
        # Extract context
        dsr_name = context.get("dsr_name", "DSR")
        coaching_type = context.get("type", "outlet_visit")
        logger.info(f"   ├── Type: {coaching_type}")
        logger.info(f"   ├── DSR: {dsr_name}")
        strengths = context.get("strengths", [])
        dev_areas = context.get("dev_areas", [])
        outlet_type = context.get("outlet_type", "outlet")
        outlet_name = context.get("outlet_name", "")
        lipb = context.get("lipb", 0)
        target_lipb = context.get("target_lipb", 3)
        issues = context.get("issues", [])
        top_skus = context.get("top_skus", [])
        rule_tips = context.get("rule_tips", [])
        coaching_type = context.get("type", "outlet_visit")  # outlet_visit, morning, end_of_day

        # Build prompt based on coaching type
        if coaching_type == "morning":
            prompt = f"""
You are a supportive sales coach for a beverage DSR in Sri Lanka.

Generate a morning greeting message in Sinhala for {dsr_name}.

Today's plan:
- Outlets to visit: {context.get('outlets_count', 0)}
- Priority outlets: {context.get('priority_count', 0)}
- Target: LKR {context.get('target', 0)}

Guidelines:
- Be encouraging and positive
- Keep it brief (2-3 sentences max)
- Use natural, conversational Sinhala
- Include a motivating closing

Generate ONLY the message, no explanations.
"""

        elif coaching_type == "end_of_day":
            prompt = f"""
You are a supportive sales coach for a beverage DSR in Sri Lanka.

Generate an end-of-day summary message in Sinhala for {dsr_name}.

Performance:
- Route adherence: {context.get('route_adherence', 0)}%
- Target achievement: {context.get('target_achievement', 0)}%
- Outlets visited: {context.get('visited', 0)} / {context.get('planned', 0)}
- Outlets ahead: {context.get('ahead', 0)}
- Outlets behind: {context.get('behind', 0)}

Guidelines:
- Congratulate achievements
- Be encouraging about areas to improve
- Keep it brief (3-4 sentences max)
- Use natural Sinhala
- End with motivation for tomorrow

Generate ONLY the message, no explanations.
"""

        else:  # outlet_visit coaching
            issues_str = ", ".join(issues) if issues else "none noted"
            strengths_str = ", ".join(strengths) if strengths else "Customer Handling"
            skus_str = ", ".join([sku.get("sku_name", "") for sku in top_skus[:3]]) if top_skus else "Coca-Cola, Sprite"

            prompt = f"""
You are a supportive sales coach for a beverage DSR in Sri Lanka.

Generate coaching tips in Sinhala for {dsr_name} visiting {outlet_name} ({outlet_type}).

DSR Profile:
- Strengths: {strengths_str}
- Development areas: {", ".join(dev_areas) if dev_areas else "None"}

Outlet Context:
- Current LIPB: {lipb} (Target: {target_lipb})
- Gap: {target_lipb - lipb} SKUs needed
- Issues: {issues_str}
- Top 3 SKUs: {skus_str}

Task:
Generate 3-4 SHORT, actionable coaching tips in natural Sinhala.

Guidelines:
- Be specific and actionable
- Reference the DSR's strengths positively
- Suggest which SKUs to push
- Address the LIPB gap
- Keep each tip to 1 sentence
- Use encouraging tone
- Format as bullet points (use • or -)

Generate ONLY the tips in Sinhala, no other text.
"""

        # Call Gemini
        logger.info("   ├── Calling Gemini LLM...")
        response = llm.invoke(prompt)
        logger.info(f"   ├── Raw response type: {type(response.content)}")

        # Handle response content (could be string, list, or list of dicts)
        if isinstance(response.content, list):
            # Handle list of dicts like [{'type': 'text', 'text': '...'}]
            parts = []
            for item in response.content:
                if isinstance(item, dict):
                    # Extract text from dict format
                    parts.append(item.get('text', str(item)))
                else:
                    parts.append(str(item))
            coaching_message = " ".join(parts).strip()
        elif isinstance(response.content, dict):
            # Handle single dict format
            coaching_message = response.content.get('text', str(response.content)).strip()
        else:
            coaching_message = str(response.content).strip()

        # Validate response
        if not coaching_message or len(coaching_message) < 10:
            raise ValueError("Generated message too short")

        logger.info(f"Generated AI coaching ({coaching_type}): {coaching_message[:100]}...")
        return coaching_message

    except Exception as e:
        logger.error(f"Error in generate_ai_coaching_tool: {e}")

        # Fallback messages in Sinhala
        if coaching_type == "morning":
            return f"සුභ උදෑසනක්! අද දවස හොඳට ක්‍රියාත්මක වෙන්න. ඔබට හැකියි! 💪"
        elif coaching_type == "end_of_day":
            return f"අද දවස හොඳට කටයුතු කළා! හෙට තව හොඳින් කරමු! 👍"
        else:
            return f"""
• LIPB වැඩි කරන්න SKU 2-3ක් විකුණන්න try කරන්න
• ඔබේ Customer Handling skills use කරන්න
• Top SKUs promote කරන්න
"""
