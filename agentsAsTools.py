import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

# Specialist agents
note_taking_agent = Agent(
    name="Note Manager",
    instructions="You help users take and organize notes efficiently.",
    # In a real application, this agent would have note-taking tools
)

task_management_agent = Agent(
    name="Task Manager",
    instructions="You help users manage tasks, deadlines, and priorities.",
    # In a real application, this agent would have task management tools
)

# Coordinator agent that uses specialists (agents) as tools
productivity_assistant = Agent(
    name="Productivity Assistant",
    instructions="""You are a productivity assistant that helps users organize their work and personal life.

   For note-taking questions or requests, use the note_taking tool.
   For task and deadline management, use the task_management tool.

   Help the user decide which tool is appropriate based on their request,
   and coordinate between different aspects of productivity.
   """,
    tools=[
        note_taking_agent.as_tool(
            tool_name="note_taking",
            tool_description="For taking, organizing, and retrieving notes and information"
        ),
        task_management_agent.as_tool(
            tool_name="task_management",
            tool_description="For managing tasks, setting deadlines, and tracking priorities"
        )
    ]
)


async def main():
    runner = Runner()

    result = await runner.run(productivity_assistant, "I need to keep track of my project deadlines")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

# When delegating tasks to other agents as tools, the initial agent (productivity_agent) will decide which tool to use.
# Eg, a more specialised agent,
