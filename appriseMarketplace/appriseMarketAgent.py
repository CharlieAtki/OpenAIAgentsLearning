import asyncio
from dotenv import load_dotenv
import os
from agents import Agent, Runner, function_tool
from pymongo import MongoClient

# Loading the .env variables from the .env file
load_dotenv()

# Get the value
MONGO_URI = os.getenv("MONGO_URI")

# Replace with your connection string
client = MongoClient(MONGO_URI)

# Access a database
db = client["AppriseMarketplaceDatabase"]


@function_tool
def get_listing_count() -> str:
    """Get the current number of active listings on Apprise Marketplace."""
    collection = db["listings"]
    result = collection.count_documents({})
    # This would normally connect to your database - using mock data for demo
    return f"There are currently {result} active listings on Apprise Marketplace."


@function_tool
def get_popular_listing() -> str:
    collection = db["bookings"]

    pipeline = [
        {
            "$group": {
                "_id": "$booking",
                "count": {"$sum": 1},
                "destinationName": {"$first": "$destinationName"}  # ✅ using $first to include it
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]

    result = list(collection.aggregate(pipeline))

    if result:
        top = result[0]
        return f"Most popular booking: {top['destinationName']} ({top['_id']}) with {top['count']} bookings."
    else:
        return "No bookings found."


business_information_agent = Agent(
    name="Business Information Agent",
    instructions="""Your are a business information specialist who helps customer understanding what Apprise 
    Marketplace is about. Focus on providing information, including; what listings are, what Apprise Marketplace is 
    about, Why the customer should use the service. If asked about technical problems or account settings, 
    explain that you specialise in customer information only.""",
    model="gpt-4.1-mini",
    tools=[get_listing_count, get_popular_listing]
)

# Create specialist agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="""You are a billing specialist who helps customers with payment issues.
   Focus on resolving billing inquiries, subscription changes, and refund requests.
   If asked about technical problems or account settings, explain that you specialize
   in billing and payment matters only.""",
    model="gpt-4.1-mini",
)

technical_agent = Agent(
    name="Technical Agent",
    instructions="""You are a technical support specialist who helps with product issues.
   Assist users with troubleshooting, error messages, and how-to questions.
   Focus on resolving technical problems only.""",
    model="gpt-4.1-mini",
)

# Create a triage agent that can hand off to specialists
triage_agent = Agent(
    name="Customer Service",
    instructions="""You are the initial customer service contact who helps direct
   customers to the right specialist.

   If the customer has billing or payment questions, hand off to the Billing Agent.
   If the customer has technical problems or how-to questions, hand off to the Technical Agent.
   If the customer has inquires about Apprise Marketplace or its listings, hand off to the Business Information Agent.
   For general inquiries or questions about products, you can answer directly.

   Always be polite and helpful, and ensure a smooth transition when handing off to specialists.""",
    model="gpt-4.1-mini",
    handoffs=[billing_agent, technical_agent, business_information_agent],  # Direct handoff to specialist agents
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
    asyncio.run(handle_customer_request("Okay, do you have any listing recommendations from the marketplace"))
