from agents import Agent
from agents.mcp import MCPServer

agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant and would use tools to help the user""",
    mcp_servers=[mpc_server],
)