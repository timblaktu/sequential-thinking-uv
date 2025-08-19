#!/usr/bin/env python3
"""
Main entry point for the Sequential Thinking MCP Server.
"""

from .server_fastmcp import mcp


def main():
    """Main entry point for the Sequential Thinking MCP Server."""
    mcp.run()


if __name__ == "__main__":
    main()