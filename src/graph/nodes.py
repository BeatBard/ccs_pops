"""
LangGraph Nodes
Each node handles a specific conversation flow
"""

from langchain_core.messages import HumanMessage, AIMessage
from .state import ConversationState, States
from ..tools import (
    get_daily_plan_tool,
    get_outlet_info_tool,
    get_lipb_tracking_tool,
    get_top_skus_tool,
    get_coaching_tips_tool,
    mark_visit_tool,
    calculate_metrics_tool,
    generate_ai_coaching_tool,
)
from ..whatsapp import TemplateType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def morning_checkin_node(state: ConversationState) -> ConversationState:
    """Handle morning check-in flow"""
    logger.info("=" * 50)
    logger.info("🌅 MORNING CHECK-IN NODE STARTED")
    logger.info("=" * 50)
    
    try:
        dsr_name = state["dsr_name"]
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"📋 DSR: {dsr_name} | Date: {today}")

        # Get daily plan using tool
        logger.info("🔧 TOOL CALL: get_daily_plan_tool")
        logger.info(f"   ├── Input: dsr_name={dsr_name}, date={today}")
        plan_result = get_daily_plan_tool.invoke({"dsr_name": dsr_name, "date": today})
        logger.info(f"   └── Result: {plan_result.get('total_count', 0)} outlets, target={plan_result.get('total_target', 0)}")

        if plan_result.get("total_count", 0) == 0:
            logger.info("📭 No outlets planned for today")
            message = f"සුභ උදෑසනක්! අද ඔබට visit කරන්න outlets නැහැ. විවේක දිනයක් enjoy කරන්න! 😊"
        else:
            # Generate AI greeting
            context = {
                "type": "morning",
                "dsr_name": dsr_name,
                "outlets_count": plan_result["total_count"],
                "priority_count": plan_result["priority_count"],
                "target": plan_result["total_target"],
            }
            
            logger.info("🔧 TOOL CALL: generate_ai_coaching_tool")
            logger.info(f"   ├── Context type: morning")
            logger.info(f"   ├── Outlets: {context['outlets_count']}, Priority: {context['priority_count']}")
            ai_greeting = generate_ai_coaching_tool.invoke({"context": context})
            logger.info(f"   └── AI Response: {ai_greeting[:100]}..." if len(str(ai_greeting)) > 100 else f"   └── AI Response: {ai_greeting}")

            # Add plan details
            breakdown = plan_result.get("breakdown", {})
            breakdown_text = " | ".join([f"{k}: {v}" for k, v in breakdown.items()])
            
            # Get outlet list for display
            outlets = plan_result.get("outlets", [])
            outlet_list = ""
            for i, outlet in enumerate(outlets, 1):
                outlet_id = outlet.get("outlet_id", "")
                outlet_name = outlet.get("outlet_name", "Unknown")
                priority = "⭐" if outlet.get("priority") == "Yes" else ""
                outlet_list += f"\n   {i}. {outlet_id} - {outlet_name} {priority}"
            
            logger.info(f"📍 Outlets in plan: {[o.get('outlet_id') for o in outlets]}")

            message = f"""{ai_greeting}

📋 අද status එක:
Plan කරපු outlets: {plan_result['total_count']}
Priority outlets: {plan_result['priority_count']}
Target: LKR {plan_result['total_target']:,.0f}

📍 අද visit කරන්න ඕන outlets:{outlet_list}

Breakdown: {breakdown_text}"""

            logger.info(f"📱 Will show GREETING template buttons")

        # Update state - Use GREETING template for buttons
        logger.info("✅ MORNING CHECK-IN NODE COMPLETED")
        logger.info(f"   ├── New state: ACTIVE")
        logger.info(f"   ├── Message length: {len(message)} chars")
        logger.info(f"   └── Template: {TemplateType.GREETING.value}")
        logger.info("=" * 50)
        
        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.ACTIVE,
            "previous_state": state["current_state"],
            "daily_plan": plan_result,
            "morning_checkin_done": True,
            "template_type": TemplateType.GREETING.value,  # Show greeting buttons
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in morning_checkin_node: {e}")
        error_msg = f"සමාවෙන්න, දෝෂයක් සිදු විය: {str(e)}"
        return {
            "messages": state["messages"] + [AIMessage(content=error_msg)],
            "template_type": TemplateType.GREETING.value,  # Show greeting buttons even on error
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }


def outlet_arrival_node(state: ConversationState) -> ConversationState:
    """Handle outlet arrival and provide coaching"""
    logger.info("=" * 50)
    logger.info("📍 OUTLET ARRIVAL NODE STARTED")
    logger.info("=" * 50)

    try:
        # Extract outlet ID from last message
        last_message = state["messages"][-1].content.strip()
        logger.info(f"📝 User message: {last_message}")

        # Check if numeric selection from outlet list
        if state.get("current_state") == States.OUTLET_SELECT and last_message.isdigit():
            selection_num = int(last_message)
            daily_plan = state.get("daily_plan")

            if daily_plan and daily_plan.get("outlets"):
                outlets = daily_plan["outlets"]
                if 1 <= selection_num <= len(outlets):
                    selected_outlet = outlets[selection_num - 1]
                    outlet_id = selected_outlet.get("outlet_id")
                    logger.info(f"🔢 NUMERIC SELECTION: #{selection_num} → {outlet_id}")
                else:
                    logger.warning(f"⚠️ Invalid selection: {selection_num} (max: {len(outlets)})")
                    message = f"කරුණාකර 1 සිට {len(outlets)} අතර අංකයක් ඇතුළත් කරන්න"
                    return {
                        "messages": state["messages"] + [AIMessage(content=message)],
                        "template_type": TemplateType.GREETING.value,
                        "buttons": None,
                        "updated_at": datetime.now().isoformat()
                    }
            else:
                logger.error("⚠️ No daily plan available for selection")
                outlet_id = None
        else:
            # Extract from text (e.g., "At SD0001")
            outlet_id = extract_outlet_id(last_message)
            logger.info(f"🔍 Extracted outlet ID: {outlet_id}")

        if not outlet_id:
            logger.warning("⚠️ No valid outlet ID found in message")
            message = "කරුණාකර outlet ID එක නිවැරදිව ඇතුළත් කරන්න (උදා: SD0001)"
            return {
                "messages": state["messages"] + [AIMessage(content=message)],
                "template_type": TemplateType.GREETING.value,
                "buttons": None,
                "updated_at": datetime.now().isoformat()
            }

        dsr_name = state["dsr_name"]
        logger.info(f"👤 DSR: {dsr_name} | Outlet: {outlet_id}")

        # Call multiple tools to gather context
        logger.info("🔧 TOOL CALL: get_outlet_info_tool")
        logger.info(f"   └── Input: outlet_id={outlet_id}")
        outlet_info = get_outlet_info_tool.invoke({"outlet_id": outlet_id})
        logger.info(f"   └── Result: {outlet_info.get('outlet_name', 'Unknown')} ({outlet_info.get('outlet_type', 'Unknown')})")
        
        logger.info("🔧 TOOL CALL: get_lipb_tracking_tool")
        logger.info(f"   └── Input: dsr_name={dsr_name}, outlet_id={outlet_id}")
        lipb_data = get_lipb_tracking_tool.invoke({"dsr_name": dsr_name, "outlet_id": outlet_id})
        logger.info(f"   └── Result: LIPB avg={lipb_data.get('avg_lipb', 0)}, target={lipb_data.get('target_lipb', 3)}")
        
        logger.info("🔧 TOOL CALL: get_top_skus_tool")
        logger.info(f"   └── Input: outlet_id={outlet_id}, top_n=5")
        top_skus = get_top_skus_tool.invoke({"outlet_id": outlet_id, "top_n": 5})
        logger.info(f"   └── Result: {len(top_skus)} SKUs returned")

        # Get rule-based tips
        coaching_category = "Upselling" if lipb_data.get("needs_improvement") else "Performance"
        logger.info("🔧 TOOL CALL: get_coaching_tips_tool")
        logger.info(f"   └── Input: category={coaching_category}")
        rule_tips = get_coaching_tips_tool.invoke({
            "category": coaching_category,
            "situation": "Low LIPB" if lipb_data.get("needs_improvement") else "",
            "dsr_strength": state.get("dsr_profile", {}).get("strengths", ["Customer Handling"])[0] if state.get("dsr_profile") else "Customer Handling"
        })
        logger.info(f"   └── Result: {len(rule_tips)} tips returned")

        # Generate AI coaching
        ai_context = {
            "type": "outlet_visit",
            "dsr_name": dsr_name,
            "strengths": ["Customer Handling"],  # From DSR profile
            "dev_areas": ["Route Planning"],
            "outlet_type": outlet_info.get("outlet_type", "outlet"),
            "outlet_name": outlet_info.get("outlet_name", outlet_id),
            "lipb": lipb_data.get("avg_lipb", 0),
            "target_lipb": lipb_data.get("target_lipb", 3),
            "issues": ["visibility"] if "visibility" in str(outlet_info) else [],
            "top_skus": top_skus,
            "rule_tips": rule_tips
        }

        logger.info("🔧 TOOL CALL: generate_ai_coaching_tool")
        logger.info(f"   └── Context type: outlet_visit")
        ai_coaching = generate_ai_coaching_tool.invoke({"context": ai_context})
        logger.info(f"   └── AI Response: {str(ai_coaching)[:100]}..." if len(str(ai_coaching)) > 100 else f"   └── AI Response: {ai_coaching}")

        # Format message with clear sales submission instructions
        message = f"""📍 {outlet_info.get('outlet_name', outlet_id)} - {outlet_info.get('outlet_type', '')}

📊 LIPB Status:
• Average: {lipb_data.get('avg_lipb', 0)} (Target: {lipb_data.get('target_lipb', 3)})
• Last visit: {lipb_data.get('last_lipb', 0)} SKUs
• Trend: {lipb_data.get('lipb_trend', 'Stable')}

🔝 Top SKUs:
{format_skus(top_skus[:3])}

💡 Coaching Tips:
{ai_coaching}

ඔබට හැකියි! 💪

━━━━━━━━━━━━━━━━━━━━
💰 *විකුණුම් Record කරන්න:*
Visit එක ඉවර වුණාම මෙසේ type කරන්න:
👉 Sales 15000
👉 Sales 25000
━━━━━━━━━━━━━━━━━━━━"""

        # Update state - Show GREETING template for next actions
        logger.info("✅ OUTLET ARRIVAL NODE COMPLETED")
        logger.info(f"   ├── New state: COACHING")
        logger.info(f"   ├── Current outlet: {outlet_id}")
        logger.info(f"   └── Template: {TemplateType.GREETING.value}")
        logger.info("=" * 50)
        
        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.COACHING,
            "previous_state": state["current_state"],
            "current_outlet": outlet_id,
            "template_type": TemplateType.GREETING.value,  # Show greeting buttons for next action
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in outlet_arrival_node: {e}")
        error_msg = f"සමාවෙන්න, දෝෂයක් සිදු විය: {str(e)}"
        return {
            "messages": state["messages"] + [AIMessage(content=error_msg)],
            "template_type": TemplateType.GREETING.value,
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }


def visit_complete_node(state: ConversationState) -> ConversationState:
    """Handle visit completion"""
    logger.info("=" * 50)
    logger.info("💰 VISIT COMPLETE NODE STARTED")
    logger.info("=" * 50)
    
    try:
        # Extract sales value from message
        last_message = state["messages"][-1].content
        logger.info(f"📝 User message: {last_message}")
        sales_value = extract_sales_value(last_message)
        logger.info(f"💵 Extracted sales value: {sales_value}")

        if sales_value is None:
            logger.warning("⚠️ No valid sales value found")
            message = "විකුණුම් අගය ඇතුළත් කරන්න (උදා: Sales 13500)"
            return {
                "messages": state["messages"] + [AIMessage(content=message)],
                "template_type": TemplateType.GREETING.value,
                "buttons": None,
                "updated_at": datetime.now().isoformat()
            }

        dsr_name = state["dsr_name"]
        outlet_id = state.get("current_outlet")
        logger.info(f"👤 DSR: {dsr_name} | Current outlet: {outlet_id}")

        if not outlet_id:
            logger.warning("⚠️ No current outlet set")
            message = "කරුණාකර පළමුව outlet එකකට visit කරන්න"
            return {
                "messages": state["messages"] + [AIMessage(content=message)],
                "template_type": TemplateType.GREETING.value,
                "buttons": None,
                "updated_at": datetime.now().isoformat()
            }

        # Mark visit
        logger.info("🔧 TOOL CALL: mark_visit_tool")
        logger.info(f"   ├── Input: outlet_id={outlet_id}, sales={sales_value}")
        mark_result = mark_visit_tool.invoke({
            "dsr_name": dsr_name,
            "outlet_id": outlet_id,
            "sales_value": sales_value,
            "productive": sales_value > 0
        })
        logger.info(f"   └── Result: {mark_result}")

        # Update outlets visited
        outlets_visited = state.get("outlets_visited_today", [])
        if outlet_id not in outlets_visited:
            outlets_visited.append(outlet_id)

        # Get remaining outlets from daily plan
        daily_plan = state.get("daily_plan", {})
        total_planned = daily_plan.get("total_count", 0)
        remaining = total_planned - len(outlets_visited)

        message = f"""✅ Visit සාර්ථකයි!

📍 Outlet: {outlet_id}
💰 Sales: LKR {sales_value:,.0f}
🕐 Time: {mark_result.get('time', '')}

━━━━━━━━━━━━━━━━━━━━
📊 අද Progress:
• Visit කළ outlets: {len(outlets_visited)} / {total_planned}
• ඉතිරි outlets: {remaining}
━━━━━━━━━━━━━━━━━━━━

{'🎉 හොඳයි! ඊළඟ outlet එකට යමු!' if remaining > 0 else '🏆 සියලු outlets visit කළා! දවස අවසන් කරන්න "End day" type කරන්න.'}"""

        logger.info("✅ VISIT COMPLETE NODE COMPLETED")
        logger.info(f"   ├── Outlet: {outlet_id}")
        logger.info(f"   ├── Sales: LKR {sales_value:,.0f}")
        logger.info(f"   └── Template: {TemplateType.GREETING.value}")
        logger.info("=" * 50)

        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.ACTIVE,
            "previous_state": state["current_state"],
            "current_outlet": None,
            "outlets_visited_today": outlets_visited,
            "template_type": TemplateType.GREETING.value,  # Show greeting buttons for next action
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in visit_complete_node: {e}")
        error_msg = f"සමාවෙන්න, දෝෂයක් සිදු විය: {str(e)}"
        return {
            "messages": state["messages"] + [AIMessage(content=error_msg)],
            "template_type": TemplateType.GREETING.value,
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }


def end_of_day_node(state: ConversationState) -> ConversationState:
    """Handle end of day summary"""
    logger.info("=" * 50)
    logger.info("🌙 END OF DAY NODE STARTED")
    logger.info("=" * 50)
    
    try:
        dsr_name = state["dsr_name"]
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"👤 DSR: {dsr_name} | Date: {today}")

        # Calculate metrics
        logger.info("🔧 TOOL CALL: calculate_metrics_tool")
        logger.info(f"   └── Input: dsr_name={dsr_name}, date={today}")
        metrics = calculate_metrics_tool.invoke({"dsr_name": dsr_name, "date": today})
        logger.info(f"   └── Result: visited={metrics.get('visited_count', 0)}/{metrics.get('planned_count', 0)}, sales={metrics.get('total_sales', 0)}")

        # Generate AI summary
        ai_context = {
            "type": "end_of_day",
            "dsr_name": dsr_name,
            "route_adherence": metrics.get("route_adherence", 0),
            "target_achievement": metrics.get("target_achievement", 0),
            "visited": metrics.get("visited_count", 0),
            "planned": metrics.get("planned_count", 0),
            "ahead": metrics.get("outlets_ahead_count", 0),
            "behind": metrics.get("outlets_behind_count", 0),
        }

        logger.info("🔧 TOOL CALL: generate_ai_coaching_tool")
        logger.info(f"   └── Context type: end_of_day")
        ai_summary = generate_ai_coaching_tool.invoke({"context": ai_context})
        logger.info(f"   └── AI Response: {str(ai_summary)[:100]}..." if len(str(ai_summary)) > 100 else f"   └── AI Response: {ai_summary}")

        # Format message
        message = f"""🌙 අද දවස හරි!

{ai_summary}

📊 Summary:
• Outlets: {metrics['visited_count']} / {metrics['planned_count']}
• Route adherence: {metrics['route_adherence']}%
• Target achievement: {metrics['target_achievement']}%
• Productive visits: {metrics['productive_visits']}

📈 Performance:
• Ahead: {metrics['outlets_ahead_count']} outlets
• Behind: {metrics['outlets_behind_count']} outlets

Total sales: LKR {metrics['total_sales']:,.0f}

හෙට තව හොඳට කරමු! විශ්‍රාම ගන්න. 😊"""

        logger.info("✅ END OF DAY NODE COMPLETED")
        logger.info(f"   ├── Visited: {metrics['visited_count']}/{metrics['planned_count']}")
        logger.info(f"   ├── Route adherence: {metrics['route_adherence']}%")
        logger.info(f"   ├── Target achievement: {metrics['target_achievement']}%")
        logger.info(f"   └── Total sales: LKR {metrics['total_sales']:,.0f}")
        logger.info("=" * 50)

        return {
            "messages": state["messages"] + [AIMessage(content=message)],
            "current_state": States.DAY_COMPLETE,
            "previous_state": state["current_state"],
            "end_of_day_done": True,
            "template_type": TemplateType.GREETING.value,  # Show greeting for next interaction
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error in end_of_day_node: {e}")
        error_msg = f"සමාවෙන්න, දෝෂයක් සිදු විය: {str(e)}"
        return {
            "messages": state["messages"] + [AIMessage(content=error_msg)],
            "template_type": TemplateType.GREETING.value,
            "buttons": None,
            "updated_at": datetime.now().isoformat()
        }


def error_handler_node(state: ConversationState) -> ConversationState:
    """Handle errors and unknown intents"""
    logger.info("=" * 50)
    logger.info("❓ ERROR HANDLER NODE STARTED")
    logger.info("=" * 50)
    
    # Check if user just responded with OW (ready to work)
    current_state = state.get("current_state", States.IDLE)
    last_msg = state["messages"][-1].content.lower() if state["messages"] else ""
    logger.info(f"📝 Last message: '{last_msg}'")
    logger.info(f"📊 Current state: {current_state}")
    
    if current_state == States.AWAITING_RESPONSE or "ow" in last_msg or "yes" in last_msg:
        logger.info("✅ User confirmed ready (OW/Yes) - showing next steps")
        # User is ready to start - give them guidance
        message = """✅ හොඳයි! දැන් ඔබ ready!

🚗 ඊළඟ පියවර: Outlet එකකට ගිහින් "At SD0001" type කරන්න

ඔබට හැකියි! 💪"""
        
        template_type = TemplateType.GREETING.value
    else:
        logger.info("⚠️ Unknown intent - showing help menu")
        # General help message - Show HELP template
        message = """🤔 මට තේරුණේ නැහැ. උදව්වක් ඕනද?"""
        
        template_type = TemplateType.HELP.value

    logger.info("✅ ERROR HANDLER NODE COMPLETED")
    logger.info(f"   └── Template: {template_type}")
    logger.info("=" * 50)

    return {
        "messages": state["messages"] + [AIMessage(content=message)],
        "template_type": template_type,
        "buttons": None,
        "updated_at": datetime.now().isoformat()
    }


# Helper functions
def extract_outlet_id(text: str) -> str:
    """Extract outlet ID from message"""
    import re
    match = re.search(r'SD\d{4}', text.upper())
    return match.group(0) if match else None


def extract_sales_value(text: str) -> float:
    """Extract sales value from message"""
    import re
    # Remove "sales" or "විකුණුම්" prefix first
    cleaned = re.sub(r'(?:sales|විකුණුම්)\s*', '', text.lower())
    
    # Extract all digits (handles "75 000", "75,000", "75000")
    # First try to find a number pattern with spaces, commas, or plain digits
    match = re.search(r'(\d[\d\s,]*\d|\d+)', cleaned)
    if match:
        # Remove spaces and commas to get the actual number
        number_str = match.group(1).replace(' ', '').replace(',', '')
        return float(number_str)
    return None


def format_skus(skus: list) -> str:
    """Format SKU list for display"""
    if not skus:
        return "• No data"

    formatted = []
    for sku in skus:
        name = sku.get("sku_name", "Unknown")
        status = sku.get("stock_status", "")
        stock_emoji = "⚠️" if "LOW" in status.upper() or "OUT" in status.upper() else "✅"
        formatted.append(f"• {name} {stock_emoji}")

    return "\n".join(formatted)
