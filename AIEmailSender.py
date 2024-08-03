import os
import requests # type: ignore
import replicate # type: ignore

# Specify the Mailgun API endpoint and credentials
MAILGUN_API_ENDPOINT = os.getenv('MAILGUN_API_ENDPOINT')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')

# Verify that the MAILGUN_API_KEY is being read correctly
if MAILGUN_API_KEY is None:
    raise ValueError("MAILGUN_API_KEY environment variable not set")

def generate_email_content(combined_prompt):
    """
    Generate email content using the Replicate model based on the provided prompt.
    
    Parameters:
    combined_prompt (str): The combined prompt including preprompt and user input.
    
    Returns:
    str: Generated email content.
    """
    input_params = {
        "top_p": 1,
        "prompt": combined_prompt,
        "temperature": 0.5,
        "max_new_tokens": 500,
        "min_new_tokens": -1
    }

    # Run the model and capture the result
    result = replicate.run(
        "meta/llama-2-70b-chat",
        input=input_params
    )

    # Join the list of characters into a string if it's in that format
    if isinstance(result, list):
        return ''.join(result)
    else:
        return result

def send_email(Users_email, to_address, email_subject, email_body):
    """
    Send an email using the Mailgun API.
    
    Parameters:
    to_address (str): Recipient email address.
    email_subject (str): Subject of the email.
    email_body (str): Body content of the email.
    """
    data = {
        'from': Users_email,
        'to': to_address,
        'subject': email_subject,
        'text': email_body
    }

    response = requests.post(
        MAILGUN_API_ENDPOINT,
        auth=('api', MAILGUN_API_KEY),
        data=data
    )

    if response.status_code == 200:
        print('Email sent successfully!')
    else:
        print(f'An error occurred while sending the email: {response.status_code} - {response.text}')

# Read pre-prompt from file
with open('preprompt.txt', 'r') as file:
    pre_prompt = file.read().strip()

while True:
    Users_email = input("Enter the email address you want to use:\n")
    recipient_email = input("Enter the email you want to send to:\n")
    email_subject = input("Enter the subject of the email:\n")
    user_prompt = input("Enter what you want the email to be about:\n")
    if recipient_email and email_subject and user_prompt and Users_email:
        break
    print("Make sure you enter a your email address, the destination email address, the email subject, and the email prompt")

combined_prompt = f"{pre_prompt} {user_prompt}"

email_content = generate_email_content(combined_prompt)

print("Generated Email Content:\n", email_content)

send_email(Users_email, recipient_email, email_subject, email_content)
