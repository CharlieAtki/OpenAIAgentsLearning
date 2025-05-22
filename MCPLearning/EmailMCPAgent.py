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

agent = Agent(
    name="EmailAssistant",
    model="gpt-4.1-mini", # Or your preferred model
    instructions="""You are an assistant that can send emails. When asked to send an email, use the provided send_email_logic tool to send an email.
    You will need to structure the paramaters of the email correctly.""",
    tools=[get_time, send_email_logic], # And any other tools
    output_type=OutgoingEmail
)

async def handle_request(request):
    result = await Runner.run(agent, request)
    print(result.final_output)


# Stating the runtime when the file is run
# asycio ensures that the application will run asynchronously
if __name__ == '__main__':
    asyncio.run(handle_request(request=""" Hello, I need to send of an email about the new product launch.
    Please send an email using the tools provided. The new product is called AI agents and quickly explain what the MCP protocol provides.
    
    The recipient's email address is charlie06atkinson@gmail.com.
    """))