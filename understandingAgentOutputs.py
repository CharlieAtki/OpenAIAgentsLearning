import asyncio
from pydantic import BaseModel
from typing import List, Optional
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


# Define person data model (Using pydantic??)
class Person(BaseModel):
    name: str
    role: Optional[str]
    contact: Optional[str]


# Define meeting data model
class Meeting(BaseModel):
    date: str
    time: str
    location: Optional[str]
    duration: Optional[str]


# Define task data model
class Task(BaseModel):
    description: str
    assignee: Optional[str]
    deadline: Optional[str]
    priority: Optional[str]


# Define the complete email data model
class EmailData(BaseModel):
    subject: str
    sender: Person
    recipients: List[Person]
    main_points: List[str]
    meetings: List[Meeting]
    tasks: List[Task]
    next_steps: Optional[str]


# Create an email extraction agent with structured output
email_extractor = Agent(
    name="Email Extractor",
    instructions="""You are an assistant that extracts structured information from emails.

   When given an email, carefully identify:
   - Subject and main points
   - People mentioned (names, roles, contact info)
   - Meetings (dates, times, locations)
   - Tasks or action items (with assignees and deadlines)
   - Next steps or follow-ups

   Extract this information as structured data. If something is unclear or not mentioned,
   leave those fields empty rather than making assumptions.
   """,
    output_type=EmailData,  # This tells the agent to return data in EmailData format
)

sample_email = """
   From: Alex Johnson <alex.j@techcorp.com>
   To: Team Development <team-dev@techcorp.com>
   CC: Sarah Wong <sarah.w@techcorp.com>, Miguel Fernandez <miguel.f@techcorp.com>
   Subject: Project Phoenix Update and Next Steps
   
   Hi team,
   
   I wanted to follow up on yesterday's discussion about Project Phoenix and outline our next steps.
   
   Key points from our discussion:
   - The beta testing phase has shown promising results with 85% positive feedback
   - We're still facing some performance issues on mobile devices
   - The client has requested additional features for the dashboard
   
   Let's schedule a follow-up meeting this Friday, June 15th at 2:00 PM in Conference Room B. The meeting should last about 1.5 hours, and we'll need to prepare the updated project timeline.
   
   Action items:
   1. Sarah to address the mobile performance issues by June 20th (High priority)
   2. Miguel to create mock-ups for the new dashboard features by next Monday
   3. Everyone to review the beta testing feedback document and add comments by EOD tomorrow
   
   If you have any questions before Friday's meeting, feel free to reach out.
   
   Best regards,
   Alex Johnson
   Senior Project Manager
   (555) 123-4567
"""


async def process_email(email_text):
    result = await Runner.run(email_extractor, f"Please extract information from this email:\n\n{email_text}")
    result = result.final_output
    print(f"Subject: {result.subject}")
    print(f"From: {result.sender.name} ({result.sender.role})")
    print("\nMain points:")
    for point in result.main_points:
        print(f"- {point}")

    print("\nMeetings:")
    for meeting in result.meetings:
        print(f"- {meeting.date} at {meeting.time}, Location: {meeting.location}")

    print("\nTasks:")
    for task in result.tasks:
        print(f"- {task.description}")
        print(
            f"  Assignee: {task.assignee}, Deadline: {task.deadline}, Priority: {task.priority}"
        )


if __name__ == "__main__":
    asyncio.run(process_email(sample_email))
