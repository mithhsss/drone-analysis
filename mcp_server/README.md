# Drone India Intelligence — MCP Server

## Overview

This MCP server exposes 4 drone intelligence tools to Claude Desktop via the Model Context Protocol. All tools are powered by a Pinecone RAG system using Indian drone regulations, specifications, and business data.

## Running the Server

```bash
python -m mcp_server.server
```

## Claude Desktop Configuration

Add this block to your Claude Desktop config file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "drone-india-intelligence": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\Mithul\\Desktop\\drone-intelligence"
    }
  }
}
```

## Available Tools

### 1. `flight_time_calculator`

Calculates estimated drone flight time based on battery, weight, payload, and weather.

**Example Input:**
```json
{
  "battery_mah": 5000,
  "drone_weight_kg": 1.5,
  "payload_kg": 0.5,
  "wind_speed_kmh": 10,
  "temperature_celsius": 25
}
```

**Example Output:**
```json
{
  "estimated_flight_time_minutes": 18.3,
  "safe_flight_time_minutes": 15.6,
  "total_weight_kg": 2.0,
  "range_estimate_km": 10.4,
  "warnings": ["Payload of 0.5kg increases total weight to 2.0kg"],
  "rag_context": ["Drone battery efficiency specs..."]
}
```

### 2. `roi_calculator`

Calculates ROI, break-even, and profitability for drone business operations in India.

**Example Input:**
```json
{
  "use_case": "agriculture",
  "drone_cost_inr": 300000,
  "monthly_operational_cost_inr": 15000,
  "monthly_revenue_inr": 50000
}
```

**Example Output:**
```json
{
  "breakeven_months": 8.6,
  "roi_12_months_percent": 40.0,
  "verdict": "Profitable",
  "year_wise": [{"year": 1, "cumulative_profit_inr": 120000, "roi_percent": 40.0}]
}
```

### 3. `compliance_checker`

Checks Indian DGCA regulatory compliance for drone operations.

**Example Input:**
```json
{
  "drone_weight_kg": 5.0,
  "use_type": "commercial",
  "location": "Delhi",
  "has_remote_pilot_licence": true
}
```

**Example Output:**
```json
{
  "drone_category": "Small",
  "is_compliant": true,
  "required_permits": ["DGCA Registration (UIN)", "Remote Pilot Licence", "Commercial Operating Permit"],
  "missing_permits": [],
  "recommendation": "Your Small-category drone is compliant for commercial use at Delhi."
}
```

### 4. `drone_selector`

Recommends suitable drone models based on use case, budget, and requirements.

**Example Input:**
```json
{
  "use_case": "agriculture",
  "budget_inr": 200000,
  "payload_required_kg": 10.0
}
```

**Example Output:**
```json
{
  "budget_category": "Mid-range 1-5L",
  "recommendations": ["DJI Agras T30 specs...", "..."],
  "key_considerations": ["Use case: agriculture", "Payload requirement: 10.0kg"],
  "rag_sources_used": 8
}
```

## Running Tests

```bash
pytest tests/test_mcp_tools.py -v
```

Tests mock the RAG bridge so they run without a live Pinecone connection.
