from agents.mcp import MCPServerStdio
import asyncio
import os
import sys
from dotenv import load_dotenv
from typing import Optional
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from pydantic import BaseModel, EmailStr
from typing import List, Optional

from datetime import datetime
from agents import Agent, Runner, function_tool

# Pydantic model for the data required to send an email
class OutgoingEmail(BaseModel):
    """
    Represents the information needed to send an email.
    This structure would be populated by the agent when it intends to use the email sending tool.
    """
    to_emails: List[EmailStr]  # List of recipient email addresses. EmailStr provides basic validation.
    subject: str             # The subject line of the email.
    plain_text_body: str     # The plain text content of the email.
    html_body: Optional[str] = None  # Optional HTML content for the email.


# Custom tool to get the currernt time
@function_tool
async def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@function_tool
async def get_email_address() -> str:
    return "charlie06atkinson@gmail.com"

@function_tool
def send_email_logic(to_email: str, subject: str, plain_text_content: str, html_content: Optional[str] = None):
    """
    Sends an email using SendGrid.
    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        plain_text_content (str): The plain text content of the email.
        html_content (str, optional): The HTML content of the email. Defaults to None.
    Returns:
        None. Prints JSON output to stdout.
    """

    # Loading the .env variables from the .env file
    load_dotenv()

    api_key = os.environ.get('SENDGRID_API_KEY')
    from_email_address = 'juzatkia@gmail.com'  # Replace with your verified SendGrid sender email

    if not api_key:
        print(json.dumps({
            "status": "error",
            "message": "SENDGRID_API_KEY not found in environment variables."
        }))
        sys.exit(1)

    if not from_email_address: # Should be set in the script or from config
        print(json.dumps({
            "status": "error",
            "message": "Sender email address is not configured."
        }))
        sys.exit(1)

    message = Mail(
        from_email=from_email_address,
        to_emails=to_email,
        subject=subject,
        plain_text_content=plain_text_content,
        html_content=html_content  # Can be the same as plain_text_content if no HTML
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        if 200 <= response.status_code < 300:
            print(json.dumps({
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "status_code": response.status_code
            }))
            sys.exit(0)
        else:
            print(json.dumps({
                "status": "error",
                "message": "Failed to send email.",
                "status_code": response.status_code,
                "details": response.body.decode() if response.body else "No details"
            }))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"An exception occurred: {str(e)}"
        }))
        sys.exit(1)

# Loading the .env variables from the .env file
load_dotenv()

mcp_web_fetch = MCPServerStdio(
    params={
        "command": "uvx",
        "args": ["mcp-server-fetch"], # This defines what the agent should search the web
    }
)

email_agent = Agent(
    name="EmailAssistant",
    model="gpt-4.1-mini", # Or your preferred model
    instructions="""
    You are an intelligent assistant responsible for sending professional, well-formatted emails.

    You must follow these strict rules:

    1. **You must use the `get_email_addresses` tool to determine the recipient.** Do not guess or hardcode email addresses.
    2. **You must call each tool only once.** Do not repeat tool calls unnecessarily.
    3. **You must call `send_email_logic` to send the email.** This is your only valid output. Do not print or return email content as text or HTML.

    Use the tools in this sequence:
    - Call `get_time` once to retrieve relevant contextual information such as product launch dates.
    - Call `get_email_addresses` once to get the correct recipient's email.
    - Once all information is gathered, call `send_email_logic` with the full, polished email content.

    The email must:
    - Be addressed using the address from `get_email_addresses`.
    - Contain accurate and relevant information (e.g., product launch date from `get_time`).
    - Be clear, concise, and visually professional.
    - Be sent only through the `send_email_logic` tool.

    ✅ Valid: One call to each tool, with final output via `send_email_logic`.
    ❌ Invalid: Hardcoding recipients, repeating tools, or outputting raw text or HTML.

    You must only complete the task by calling `send_email_logic`. Do not output anything else.
    """
    ,
    tools=[get_time, send_email_logic, get_email_address], # And any other tools
    mcp_servers=[mcp_web_fetch],
    output_type=OutgoingEmail
)

triage_agent = Agent(
    name = "Internal Business Agent",
    instructions="""You are the internal business agent, desinged to assist employees carryout their work.
    
    If the employee requests help about emails, you can hand off to the EmailAssistant.
    
    For general inquiries or questions about products, you can answer directly.
    
    Always be polite and helpful, and ensure a smooth transition when handing off to specialists.
    """,
    mcp_servers=[ mcp_web_fetch ],
    handoffs=[email_agent]
)

async def handle_request(request):
    async with mcp_web_fetch:
        result = await Runner.run(triage_agent, request)
        print(result.final_output)


# Stating the runtime when the file is run
# asycio ensures that the application will run asynchronously
if __name__ == '__main__':
    asyncio.run(handle_request(request=  """Hello, I need to create a marketing email for the new product launch.
    Please talk about the Model Context Protocal (MCP) and the new product called AI agents.
    
    To make sure you are informed about the new protocol, please reserach the web for the latest news.
    https://modelcontextprotocol.io/introduction is a good start.
    
    Also, please include the date the new product is going to be released within the email.
    
    Include any other relevant information in the email and make sure it is clear and pretty"""))