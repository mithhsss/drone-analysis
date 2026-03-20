"""
ROI Calculator Tool for MCP
"""

def calculate_roi(investment, monthly_revenue, monthly_cost):
    # Simplified ROI calculation
    net_monthly_profit = monthly_revenue - monthly_cost
    if net_monthly_profit <= 0:
        return {"error": "Monthly costs exceed or equal revenue. No ROI possible."}
    
    months_to_breakeven = investment / net_monthly_profit
    
    # Generate timeline data for Plotly
    timeline = []
    for month in range(int(months_to_breakeven) + 6):
        cumulative_profit = (net_monthly_profit * month) - investment
        timeline.append({"month": month, "profit": cumulative_profit})
        
    return {
        "months_to_breakeven": round(months_to_breakeven, 1),
        "net_monthly_profit": net_monthly_profit,
        "timeline": timeline
    }
