#!/usr/bin/env python3
"""
Sequential Thinking MCP Server - FastMCP Version

A Python implementation of the Sequential Thinking MCP server that enables
structured problem-solving by breaking down complex issues into sequential steps,
supporting revisions, and enabling multiple solution paths through the Model Context Protocol.

Uses FastMCP for simplified server management and automatic asyncio handling.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from .models import ThoughtData, ThoughtSummary, BranchInfo, ThinkingSession


# Initialize FastMCP server
mcp = FastMCP("sequential-thinking-mcp")

# Global state for the thinking session
console = Console(stderr=True, force_terminal=True)
disable_thought_logging = os.getenv("DISABLE_THOUGHT_LOGGING", "").lower() == "true"

# Initialize thinking session
session = ThinkingSession(
    session_id=str(uuid.uuid4()),
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)


def _log_startup() -> None:
    """Log server startup message."""
    if disable_thought_logging:
        return
        
    startup_panel = Panel.fit(
        Text("Sequential Thinking MCP Server Started", style="bold green"),
        border_style="bright_blue"
    )
    console.print(startup_panel)
    console.print(f"[dim]Session ID: {session.session_id}[/dim]")
    console.print()


def _log_main_thought(thought_data: ThoughtData) -> None:
    """Log a main branch thought with rich formatting."""
    if disable_thought_logging:
        return
    
    # Create thought header
    if thought_data.is_revision:
        header = f"🔄 Revision {thought_data.thought_number}/{thought_data.total_thoughts}"
        color = "yellow"
    else:
        header = f"💭 Thought {thought_data.thought_number}/{thought_data.total_thoughts}"
        color = "bright_blue"
    
    # Create the thought panel
    thought_panel = Panel(
        Text(thought_data.thought, style="white"),
        title=header,
        border_style=color,
        width=80
    )
    
    console.print(thought_panel)
    
    # Add status indicators
    status_parts = []
    if thought_data.next_thought_needed:
        status_parts.append("[bright_green]→ More thoughts needed[/bright_green]")
    else:
        status_parts.append("[bright_red]✓ Thinking complete[/bright_red]")
    
    if thought_data.needs_more_thoughts:
        status_parts.append("[bright_yellow]📈 Expanding scope[/bright_yellow]")
    
    if status_parts:
        console.print(" ".join(status_parts))
    
    console.print()


def _log_branch_thought(thought_data: ThoughtData) -> None:
    """Log a branch thought with rich formatting."""
    if disable_thought_logging:
        return
    
    header = f"🌿 Branch: {thought_data.branch_id} ({thought_data.thought_number}/{thought_data.total_thoughts})"
    
    # Create the branch panel
    branch_panel = Panel(
        Text(thought_data.thought, style="white"),
        title=header,
        border_style="bright_magenta",
        width=80
    )
    
    console.print(branch_panel)
    
    # Add branch info
    branch_info = f"[dim]Branched from thought {thought_data.branch_from_thought}[/dim]"
    console.print(branch_info)
    
    # Add status indicators
    if thought_data.next_thought_needed:
        console.print("[bright_green]→ More thoughts needed in this branch[/bright_green]")
    else:
        console.print("[bright_red]✓ Branch complete[/bright_red]")
    
    console.print()


def _log_error(error_msg: str) -> None:
    """Log an error message with rich formatting."""
    if disable_thought_logging:
        return
        
    error_panel = Panel(
        Text(error_msg, style="bold red"),
        title="Error",
        border_style="red",
        width=80
    )
    console.print(error_panel)
    console.print()


def _handle_revision(thought_data: ThoughtData) -> None:
    """Handle a revision of a previous thought."""
    if thought_data.revises_thought and thought_data.revises_thought <= len(session.main_thoughts):
        # Replace the thought being revised
        revision_index = thought_data.revises_thought - 1
        session.main_thoughts[revision_index] = thought_data
        
        # Remove any subsequent thoughts that are now invalidated
        session.main_thoughts = session.main_thoughts[:revision_index + 1]
    else:
        # If revision target is invalid, treat as regular thought
        session.main_thoughts.append(thought_data)


def _process_thought(thought_data: ThoughtData) -> None:
    """Process a single thought and update the session state."""
    
    # Determine if this is a branch or main thought
    if thought_data.branch_id and thought_data.branch_from_thought:
        # This is a branch thought
        if thought_data.branch_id not in session.branches:
            session.branches[thought_data.branch_id] = []
        
        session.branches[thought_data.branch_id].append(thought_data)
        _log_branch_thought(thought_data)
    else:
        # This is a main branch thought
        if thought_data.is_revision and thought_data.revises_thought:
            # Handle revision
            _handle_revision(thought_data)
        else:
            # Regular thought
            session.main_thoughts.append(thought_data)
        
        _log_main_thought(thought_data)


@mcp.tool()
def think(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    isRevision: bool = False,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: bool = False
) -> str:
    """Process a sequential thinking step with support for revisions and branching.
    
    This tool facilitates a detailed, step-by-step thinking process for problem-solving 
    and analysis. Only set nextThoughtNeeded to false when truly done and a 
    satisfactory answer is reached.
    
    Args:
        thought: Your current thinking step
        nextThoughtNeeded: Whether another thought step is needed
        thoughtNumber: Current thought number (minimum 1)
        totalThoughts: Estimated total thoughts needed (minimum 1)
        isRevision: Whether this revises previous thinking
        revisesThought: Which thought is being reconsidered (minimum 1)
        branchFromThought: Branching point thought number (minimum 1)
        branchId: Branch identifier
        needsMoreThoughts: If more thoughts are needed
    
    Returns:
        Success or error message
    """
    try:
        # Create thought data with proper mapping
        thought_data = ThoughtData(
            thought=thought,
            next_thought_needed=nextThoughtNeeded,
            thought_number=thoughtNumber,
            total_thoughts=totalThoughts,
            is_revision=isRevision,
            revises_thought=revisesThought,
            branch_from_thought=branchFromThought,
            branch_id=branchId,
            needs_more_thoughts=needsMoreThoughts
        )
        
        # Process the thought
        _process_thought(thought_data)
        
        # Update session timestamp
        global session
        session.updated_at = datetime.now().isoformat()
        
        return f"✅ Processed thought {thought_data.thought_number}/{thought_data.total_thoughts}"
        
    except ValidationError as e:
        error_msg = f"Invalid thought data: {str(e)}"
        _log_error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Error processing thought: {str(e)}"
        _log_error(error_msg)
        return f"❌ {error_msg}"


@mcp.resource("thoughts://history")
def get_thought_history() -> str:
    """Complete history of all thoughts in the main branch."""
    return json.dumps(
        [thought.to_display_dict() for thought in session.main_thoughts],
        indent=2
    )


@mcp.resource("thoughts://summary")
def get_thinking_summary() -> str:
    """Summary of the entire thinking process."""
    summary = session.get_summary()
    return json.dumps(summary.dict(), indent=2)


@mcp.resource("thoughts://branches")
def get_branch_overview() -> str:
    """Overview of all branches in the thinking process."""
    branches_info = []
    for branch_id, thoughts in session.branches.items():
        branch_info = BranchInfo(
            branch_id=branch_id,
            branch_from_thought=thoughts[0].branch_from_thought or 0,
            thoughts=thoughts
        )
        branches_info.append(branch_info.dict())
    
    return json.dumps(branches_info, indent=2)


@mcp.resource("thoughts://session")
def get_complete_session() -> str:
    """Complete thinking session with all thoughts and branches."""
    return json.dumps(session.dict(), indent=2)


# Log startup when module is imported
_log_startup()


if __name__ == "__main__":
    mcp.run()