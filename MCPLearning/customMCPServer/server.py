from mcp.server.fastmcp import FastMCP
import requests

# defines the MCP sever
mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Fetches the current weather for the specified city."""
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

# run the custom MCP server
if __name__ == "__main__":
    mcp.run()
