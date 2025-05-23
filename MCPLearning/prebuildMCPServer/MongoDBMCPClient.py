import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv
import os


load_dotenv()

# Get the value
MONGO_URI = os.getenv("MONGO_URI")

async def run(mpc_server : MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="""You are a helpful assistant and would use tools to help the user""",
        mcp_servers=[mpc_server],
    )

    message = """In the AppriseMarketplaceDatabase users collection, find the user with the email 'juzatkia@gmail.com' 
    and then use that information to find the bookings made under that account. This information should be in the bookings collection.
    
    Please return the results in a easy to read format."""
    response = await Runner.run(agent, message)
    print(response.final_output)


async def main():
    async with MCPServerStdio(
        name="MongoDB Server",
        params={
            "command": "npx",
            "args": ["-y", "mongodb-mcp-server"],
            "env": {
                "MDB_MCP_CONNECTION_STRING": f"{MONGO_URI}"
            }
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