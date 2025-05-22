import os
import sys
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

def send_email_logic(to_email, subject, plain_text_content, html_content=None):
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

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({
            "status": "error",
            "message": "Missing required arguments: <to_email> <subject> <text_content> [html_content]"
        }))
        sys.exit(1)

    to_arg = sys.argv[1]
    subject_arg = sys.argv[2]
    text_content_arg = sys.argv[3]
    html_content_arg = sys.argv[4] if len(sys.argv) > 4 else text_content_arg # Use text as HTML if not provided

    send_email_logic(to_arg, subject_arg, text_content_arg, html_content_arg)