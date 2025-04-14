import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# Loading the .env variables from the .env file
load_dotenv()


async def main():
    agent = Agent(
        name="Test Agent",
        instructions="Your are a helpful agent that responds in a concise manner"
    )
    result = await Runner.run(agent, "Hello! Are you working correctly")
    print(result.final_output)


if __name__ == '__main__':
    asyncio.run(main())
