import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

async def run(mpc_server : MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="""You are a helpful assistant and would use tools to help the user""",
        mcp_servers=[mpc_server],
    )

    message = "What's the weather like today in London?"
    response = await Runner.run(agent, message)
    print(response.final_output)


async def main():
    async with MCPServerStdio(
        name="Weather Server",
        params={
            "command": "mcp",
            "args": ["run", "server.py"],
        },
        cache_tools_list=True,
    ) as server:
        tool_list = await server.list_tools()
        for tool in tool_list:
            print(f"Tool Name: {tool.name}")

        print("Starting MCP sevrer")
        await run(server)

if __name__ == "__main__":
    asyncio.run(main())

# This client connects to a custom MCP sever.