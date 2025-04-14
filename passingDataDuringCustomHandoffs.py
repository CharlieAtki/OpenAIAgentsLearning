import asyncio  # Asynchronous functions (async & await)
from pydantic import BaseModel  # Data structures (Like Mongoose Schemas for MERN Stack)
from typing import Optional
from agents import Agent, handoff, RunContextWrapper, Runner  # OpenAI Agent SDK
from dotenv import load_dotenv

load_dotenv()  # Loading the env variables from the /env file=


# Define the data structure to pass during handoff
# This helps structure the LLM / Agent's response into parsable data structures.
# Allowing for system consistency (Data can consistency be structured in the same way)
class EscalationData(BaseModel):
    reason: str
    priority: Optional[str]
    customer_tier: Optional[str]


# Handoff callback that processes the escalation data / had context of previous discussions
async def process_escalation(ctx: RunContextWrapper, input_data: EscalationData):
    print(f"[ESCALATION] Reason: {input_data.reason}")
    print(f"[ESCALATION] Priority: {input_data.priority}")
    print(f"[ESCALATION] Customer tier: {input_data.customer_tier}")

    # You might use this data to prioritize responses, alert human agents, etc.


# Create an escalation agent
escalation_agent = Agent(
    name="Escalation Agent",
    instructions="""You handle complex or sensitive customer issues that require
   special attention. Always address the customer's concerns with extra care and detail.""",
)

# Create a service agent that can escalate with context
service_agent = Agent(
    name="Service Agent",
    instructions="""You are a customer service agent who handles general inquiries.

   For complex issues, escalate to the Escalation Agent and provide:
   - The reason for escalation
   - Priority level (Low, Normal, High, Urgent)
   - Customer tier if mentioned (Standard, Premium, VIP)""",
    handoffs=[
        handoff(  # Customised handoff -> Allowing for EscalationData logging
            agent=escalation_agent,  # Defining which agent the service_agent can hand off too
            on_handoff=process_escalation,  # Callback function -> This could be used to inform customer support etc
            input_type=EscalationData,  # Pydantic EscalationData data structure (Informing the hand off agent)
        )
    ],
)


async def handle_customer_request(request):
    result = await Runner.run(service_agent, request)  # Selecting the initial agent and inputting the request
    print(result.final_output)  # final_output attribute is just the response from the LLM

# Hard coded inquiry -> This could be replaced with an input field in full-stack applications
generalInquiry = ("Hi, I am a Premium user,"
                  " but I am unable to gain access to the Premium account features."
                  " Please can you grant me access or explain how I can fix the issue")

# Initialing the handle_customer_request asynchronous function & passing the request.
if __name__ == "__main__":
    asyncio.run(handle_customer_request(generalInquiry))
