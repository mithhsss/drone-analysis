"""
MCP Server Configuration
"""

import os

MCP_SERVER_NAME = "drone-india-intelligence"
MCP_SERVER_VERSION = "1.0.0"
DEFAULT_TOP_K = 5
MAX_TOP_K = 10
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
