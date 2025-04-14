import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# Loading the .env variables from the .env file
load_dotenv()

# Create specialist agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="""You are a billing specialist who helps customers with payment issues.
   Focus on resolving billing inquiries, subscription changes, and refund requests.
   If asked about technical problems or account settings, explain that you specialize
   in billing and payment matters only.""",
)

technical_agent = Agent(
    name="Technical Agent",
    instructions="""You are a technical support specialist who helps with product issues.
   Assist users with troubleshooting, error messages, and how-to questions.
   Focus on resolving technical problems only.""",
)

# Create a triage agent that can hand off to specialists
triage_agent = Agent(
    name="Customer Service",
    instructions="""You are the initial customer service contact who helps direct
   customers to the right specialist.

   If the customer has billing or payment questions, hand off to the Billing Agent.
   If the customer has technical problems or how-to questions, hand off to the Technical Agent.
   For general inquiries or questions about products, you can answer directly.

   Always be polite and helpful, and ensure a smooth transition when handing off to specialists.""",
    handoffs=[billing_agent, technical_agent],  # Direct handoff to specialist agents
)


# Asynchronous request onto the OpenAI Agents API.
# Function takes in the user request (Hard coded at the moment)
# The function then runs the triage_agent to determine the following actions.
# Eg, pass the user to a more specialised agent
async def handle_customer_request(request):
    result = await Runner.run(triage_agent, request)
    print(result.final_output)


# Example customer inquiries -> Each example is designed to initialise an alternative response.
billing_inquiry = (
    "I was charged twice for my subscription last month. Can I get a refund?"
)
technical_inquiry = (
    "The app keeps crashing when I try to upload photos. How can I fix this? Give me the shortest solution possible."
)
general_inquiry = "What are your business hours?"

# Stating the runtime when the file is run
# asycio ensures that the application will run asynchronously
if __name__ == '__main__':
    asyncio.run(handle_customer_request(technical_inquiry))
