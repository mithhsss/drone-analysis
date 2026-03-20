"""
Drone India Intelligence — MCP Server
Main entry point. Registers all 4 tools and runs via stdio transport.
"""

import asyncio
import logging
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.config import MCP_SERVER_NAME, MCP_SERVER_VERSION, LOG_LEVEL
from mcp_server.tools.flight_time import calculate_flight_time
from mcp_server.tools.roi_calc import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_selector import select_drone

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(MCP_SERVER_NAME)

# Create MCP server
server = Server(MCP_SERVER_NAME)


# ── Tool Definitions ──────────────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="flight_time_calculator",
        description=(
            "Calculates estimated flight time for a drone given battery capacity, weight, "
            "payload, and weather conditions. Use this when the user asks how long a drone "
            "can fly, battery life, range estimates, or flight duration for any drone operation."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "battery_mah": {
                    "type": "number",
                    "description": "Battery capacity in milliamp-hours (mAh)",
                },
                "drone_weight_kg": {
                    "type": "number",
                    "description": "Drone weight in kilograms",
                },
                "payload_kg": {
                    "type": "number",
                    "description": "Payload weight in kilograms (default 0)",
                    "default": 0.0,
                },
                "wind_speed_kmh": {
                    "type": "number",
                    "description": "Wind speed in km/h (default 0)",
                    "default": 0.0,
                },
                "temperature_celsius": {
                    "type": "number",
                    "description": "Ambient temperature in Celsius (default 25)",
                    "default": 25.0,
                },
            },
            "required": ["battery_mah", "drone_weight_kg"],
        },
    ),
    Tool(
        name="roi_calculator",
        description=(
            "Calculates ROI, break-even point, and profitability for drone business operations "
            "in India. Use this when the user asks about investment returns, business viability, "
            "profit timelines, or cost-benefit analysis for any drone use case."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "use_case": {
                    "type": "string",
                    "description": "Type of drone business (e.g., agriculture, surveying, photography)",
                },
                "drone_cost_inr": {
                    "type": "number",
                    "description": "Total cost of the drone in INR",
                },
                "monthly_operational_cost_inr": {
                    "type": "number",
                    "description": "Monthly operational cost in INR",
                },
                "monthly_revenue_inr": {
                    "type": "number",
                    "description": "Expected monthly revenue in INR",
                },
                "financing_months": {
                    "type": "integer",
                    "description": "Number of months to finance the drone cost (default 0 = no financing)",
                    "default": 0,
                },
            },
            "required": ["use_case", "drone_cost_inr", "monthly_operational_cost_inr", "monthly_revenue_inr"],
        },
    ),
    Tool(
        name="compliance_checker",
        description=(
            "Checks Indian DGCA regulatory compliance for drone operations. Use this when "
            "the user asks about legality, permits, licences, registration, restrictions, or "
            "whether a specific drone operation is allowed in India."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "drone_weight_kg": {
                    "type": "number",
                    "description": "Weight of the drone in kilograms",
                },
                "use_type": {
                    "type": "string",
                    "description": "Purpose: commercial, recreational, research, etc.",
                },
                "location": {
                    "type": "string",
                    "description": "Operating location (city or coordinates)",
                },
                "has_remote_pilot_licence": {
                    "type": "boolean",
                    "description": "Whether operator has a Remote Pilot Licence (default false)",
                    "default": False,
                },
            },
            "required": ["drone_weight_kg", "use_type", "location"],
        },
    ),
    Tool(
        name="drone_selector",
        description=(
            "Recommends suitable drone models based on use case, budget, and requirements. "
            "Use this when the user asks which drone to buy, drone recommendations, or wants "
            "to compare drone options for a specific application in India."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "use_case": {
                    "type": "string",
                    "description": "Primary use case (agriculture, photography, surveying, etc.)",
                },
                "budget_inr": {
                    "type": "number",
                    "description": "Budget in INR",
                },
                "payload_required_kg": {
                    "type": "number",
                    "description": "Required payload capacity in kg (default 0)",
                    "default": 0.0,
                },
                "flight_time_required_min": {
                    "type": "number",
                    "description": "Minimum flight time required in minutes (default 20)",
                    "default": 20.0,
                },
                "indoor_use": {
                    "type": "boolean",
                    "description": "Whether the drone is for indoor use (default false)",
                    "default": False,
                },
            },
            "required": ["use_case", "budget_inr"],
        },
    ),
]

# Tool name → function mapping
TOOL_HANDLERS = {
    "flight_time_calculator": calculate_flight_time,
    "roi_calculator": calculate_roi,
    "compliance_checker": check_compliance,
    "drone_selector": select_drone,
}

# Tool name → parameter name mapping (for extracting args from input)
TOOL_PARAMS = {
    "flight_time_calculator": ["battery_mah", "drone_weight_kg", "payload_kg", "wind_speed_kmh", "temperature_celsius"],
    "roi_calculator": ["use_case", "drone_cost_inr", "monthly_operational_cost_inr", "monthly_revenue_inr", "financing_months"],
    "compliance_checker": ["drone_weight_kg", "use_type", "location", "has_remote_pilot_licence"],
    "drone_selector": ["use_case", "budget_inr", "payload_required_kg", "flight_time_required_min", "indoor_use"],
}


# ── MCP Handlers ──────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools():
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    logger.info(f"Tool called: {name} with args: {arguments}")

    if name not in TOOL_HANDLERS:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    handler = TOOL_HANDLERS[name]
    params = TOOL_PARAMS[name]

    try:
        # Extract only the known parameters
        kwargs = {k: arguments[k] for k in params if k in arguments}
        result = handler(**kwargs)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        logger.error(f"Tool '{name}' failed: {e}")
        return [TextContent(type="text", text=f"Error in {name}: {str(e)}")]


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    logger.info(f"Starting {MCP_SERVER_NAME} v{MCP_SERVER_VERSION}")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
