# Sequential-Thinking MCP Server

A Model Context Protocol (MCP) server that implements structured reasoning capabilities through sequential thinking patterns. This server provides tools for breaking down complex problems into sequential steps, maintaining context between reasoning stages, and generating structured thought processes.

## Features

- **Sequential Reasoning**: Break complex problems into manageable sequential steps
- **Context Preservation**: Maintain reasoning context across multiple interactions
- **Structured Output**: Generate well-formatted thought processes and conclusions
- **MCP Integration**: Full compatibility with Claude Desktop and other MCP clients

## Installation

### Prerequisites

- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- Git

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/USERNAME/sequential-thinking-mcp.git
cd sequential-thinking-mcp

# Create virtual environment and install dependencies
uv sync --python python3

# The binary will be available at:
.venv/bin/sequential-thinking-mcp
```

### Using Nix

This server is designed to work with the [UV MCP Server Framework](https://github.com/USERNAME/uv-mcp-servers) for Nix-based deployment:

```nix
# Add as flake input
inputs.sequential-thinking-mcp = {
  url = "github:USERNAME/sequential-thinking-mcp";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "/path/to/sequential-thinking-mcp/.venv/bin/sequential-thinking-mcp"
    }
  }
}
```

### WSL Environment

For Windows users running Claude Desktop with WSL:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "C:\\WINDOWS\\system32\\wsl.exe",
      "args": [
        "-d", "your-wsl-distro",
        "-e", "/path/to/sequential-thinking-mcp/.venv/bin/sequential-thinking-mcp"
      ],
      "env": {
        "DEBUG": "*"
      }
    }
  }
}
```

## Usage

Once configured, the sequential-thinking server provides the following tools through MCP:

### Available Tools

- `think_sequentially`: Break down a complex problem into sequential reasoning steps
- `continue_thinking`: Continue from a previous reasoning state with new information
- `summarize_thoughts`: Generate a structured summary of a reasoning process
- `evaluate_conclusion`: Assess the validity and completeness of a reasoning conclusion

### Example Usage in Claude

```
User: I need to plan a complex software migration. Can you help me think through this sequentially?

Claude: I'll use the sequential-thinking server to help break this down systematically.

[Uses think_sequentially tool to structure the migration planning process]
```

## Development

### Project Structure

```
sequential-thinking-mcp/
├── src/
│   └── sequential_thinking_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       └── models.py          # Data models for reasoning structures
├── tests/
│   └── test_server.py         # Test suite
├── .venv/                     # UV virtual environment
├── pyproject.toml             # Project configuration
├── uv.lock                    # Locked dependencies
└── README.md                  # This file
```

### Running Tests

```bash
# Run the test suite
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=sequential_thinking_mcp
```

### Development Setup

```bash
# Install in development mode
uv sync --dev

# Run the server locally for testing
uv run sequential-thinking-mcp

# Debug mode
DEBUG=* uv run sequential-thinking-mcp
```

## Technical Details

### Dependencies

- `mcp`: Model Context Protocol library
- `pydantic`: Data validation and parsing
- `asyncio`: Asynchronous I/O support

### Architecture

The server implements the MCP specification using a clean separation between:

1. **Server Layer** (`server.py`): MCP protocol handling and tool registration
2. **Model Layer** (`models.py`): Data structures for reasoning states and outputs
3. **Logic Layer**: Sequential thinking algorithms and context management

### Protocol Compliance

This server fully implements the MCP specification v0.1.0:

- **Capabilities**: Declares support for tools and resources
- **Tools**: Implements sequential reasoning tools with proper JSON schema
- **Error Handling**: Graceful error responses with meaningful messages
- **Logging**: Structured logging for debugging and monitoring

## Integration with UV MCP Framework

This server is designed to work seamlessly with the [UV MCP Server Framework](https://github.com/USERNAME/uv-mcp-servers), which provides:

- **Nix Integration**: Reproducible builds and deployment
- **Home Manager Modules**: Easy configuration management
- **Development Tools**: Streamlined development workflow
- **Template System**: Consistent project structure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## History

This server was originally developed as part of the UV MCP Server Framework project and has been extracted into its own repository to follow Nix best practices for source code separation.

## Related Projects

- [UV MCP Server Framework](https://github.com/USERNAME/uv-mcp-servers) - Nix-based infrastructure for UV MCP servers
- [Model Context Protocol](https://github.com/modelcontextprotocol/servers) - Official MCP specification and servers
- [Claude Desktop](https://claude.ai/desktop) - AI assistant with MCP support

## Support

For questions and support:

- Open an issue on GitHub
- Check the [UV MCP Framework documentation](https://github.com/USERNAME/uv-mcp-servers/docs)
- Review the [MCP specification](https://spec.modelcontextprotocol.io/)
