from agents.mcp import MCPServerStdio
import asyncio
import os
from dotenv import load_dotenv

from datetime import datetime
from agents import Agent, Runner, function_tool

# Custom tool to get the currernt time
@function_tool
async def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Loading the .env variables from the .env file
load_dotenv()

# Getting the local folder directory
current_dir = os.path.dirname(os.path.abspath(__file__))
samples_dir = os.path.join(current_dir)

# MCP local and web search config explanation:

# This version, with "args": ["mcp-server-fetch"], is the one that is intended to fetch content from the web.

# Dedicated Fetch Server: The argument mcp-server-fetch suggests that the uvx command
# is running a specialised server process whose sole purpose is to fetch content from URLs.
# This is different from the filesystem server which only interacts with local files.

# Agent Capability: When you initialise the Agent with mcp_servers=[mcp_fetch] using this configuration,
# you are equipping the agent with the ability to make requests to this web-fetching server

# The configuration line: "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],

# @modelcontextprotocol/server-filesystem: This part explicitly indicates that it's a server designed to interact with the filesystem.
# samples_dir: This argument tells the server which specific directory (and its contents) on your local system the agent is allowed to access.

# "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir], # This defines that the agent should serach through local system files
# command: npx (local config)

# ( Web search confifg)
# "command": "uvx",
# "args": ["mcp-server-fetch"],

mcp_web_fetch = MCPServerStdio(
    params={
        "command": "uvx",
        "args": ["mcp-server-fetch"], # This defines what the agent should search the web
    }
)


async def async_main():
    async with mcp_web_fetch:
        agent = Agent(name="Assistant",
          model="gpt-4.1-mini",
          instructions="You are a helpful assistant",
          mcp_servers=[mcp_web_fetch],
          tools=[get_time])

        result = await Runner.run(
            agent, """
            Please get the content of docs.replit.com/updates and summarize them. 
            Return the summary as well as the time you got the content.
            """)

        print(result.final_output)


if __name__ == "__main__":
  asyncio.run(async_main())