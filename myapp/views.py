from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Email_Content
from .serializers import EmailContentSerializer
from .serializers import EmailContentUpdateSerializer
import requests
import logging
import time
import json
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
#from .models import Manual_Email
#from .serializers import ManualEmailSerializer

# Create your views here.


# myapp/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .middleware import validate_token  # Import the validate_token middleware


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LoginUser
import json
import logging
from django.utils import timezone
 
logger = logging.getLogger(__name__)
 





@csrf_exempt  # If using CSRF tokens, adjust as necessary
@validate_token  # Apply the middleware to validate the token
def secure_view(request):
    return JsonResponse({"message": "This is a secure view protected by Azure AD authentication!"})


import jwt
from jwt import PyJWKClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import LoginUser
import json

JWKS_URL = "https://login.microsoftonline.com/a3fb180d-23c4-44c9-a241-c78109202bd3/discovery/v2.0/keys"
CLIENT_ID = ""  # Optional but recommended

@csrf_exempt
@csrf_exempt
@require_http_methods(["POST"])
def check_user(request):
    try:
        # Extract token from the Authorization header
        token = request.headers.get("Authorization")
        
        # Ensure the token starts with "Bearer "
        if not token or not token.startswith("Bearer "):
            return JsonResponse({'error': 'JWT token is missing or malformed'}, status=400)
        
        # Get the actual token part (after "Bearer ")
        token = token.split(" ")[1]
        
        if not token:
            return JsonResponse({'error': 'JWT token is missing'}, status=400)

        # Get signing key from Azure AD
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        # Decode token
        decoded = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,  # Match your registered Azure AD app
        )

        # Extract email (usually under 'upn')
        email = decoded.get('upn') or decoded.get('email')
        if not email:
            return JsonResponse({'error': 'Email not found in token'}, status=400)

        # Check DB
        if LoginUser.objects.filter(email=email).exists():
            return JsonResponse({'message': 'User exists'}, status=200)
        else:
            return JsonResponse({'error': 'User not found'}, status=404)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError as e:
        return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)





@api_view(['GET'])
def email_content_list(request):
    """
    Retrieve a list of all Email Content instances.
    """
    email_contents = Email_Content.objects.all()  # Fetch all records
    serializer = EmailContentSerializer(email_contents, many=True)  # Serialize the data
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def email_content_detail(request, pk):
    """
    Retrieve a single Email Content instance by its ID.
    """
    try:
        email_content = Email_Content.objects.get(pk=pk)  # Fetch the record by primary key
    except Email_Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = EmailContentSerializer(email_content)  # Serialize the data
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_email_content(request, pk):
    try:
        email_content = Email_Content.objects.get(pk=pk)
    except Email_Content.DoesNotExist:
        return Response({'error': 'Email content not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Update the status and mail_sent_timestamp
    email_content.status = "1"  # Change status to '1'
    email_content.mail_sent_timestamp = timezone.now()  # Set current time

    # Create a serializer with the updated instance
    serializer = EmailContentUpdateSerializer(email_content, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_access_token(client_id, client_secret, tenant_id):

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    payload = {

        'grant_type': 'client_credentials',

        'client_id': client_id,

        'client_secret': client_secret,

        'scope': 'https://graph.microsoft.com/.default'

    }
 
    try:

        response = requests.post(token_url, data=payload)

        response.raise_for_status()

        token_info = response.json()

        return token_info['access_token']

    except requests.exceptions.RequestException as e:

        logging.error(f"Exception occurred while fetching access token: {str(e)}")

        return None
 
# Synchronous function to send email reply using Microsoft Graph API

def send_reply_to_unregistered_sender(email_id, message_id, microsoft_endpoint, access_token, sender_email, subject_line, dynamic_content):

    print(message_id)
    reply_endpoint = f"{microsoft_endpoint}/v1.0/users/{email_id}/messages/{message_id}/reply"
 
    email_subject = f"RE: {subject_line}"
 
    reply_content = {

        "message": {

            "subject": email_subject,

            "body": {

                "contentType": "Text",

                "content": dynamic_content

            }

        }

    }
 
    headers = {

        "Authorization": f"Bearer {access_token}",

        "Content-Type": "application/json"

    }
 
    try:

        response = requests.post(reply_endpoint, json=reply_content, headers=headers)

        if response.status_code == 202:

            logging.info(f"Email successfully queued. Message ID: {message_id}")

            return message_id

        else:

            logging.error(f"Failed to send reply. Status: {response.status_code}, Message: {response.text}")

            return None

    except Exception as e:

        logging.error(f"Failed to send reply to message with ID: {message_id}: {str(e)}")

        return None
 
# Synchronous function to poll message status

def poll_message_status(email_id, message_id, microsoft_endpoint, access_token, max_attempts=5, wait_seconds=10):

    message_status_endpoint = f"{microsoft_endpoint}/v1.0/users/{email_id}/messages/{message_id}"
 
    headers = {

        "Authorization": f"Bearer {access_token}"

    }
 
    for attempt in range(max_attempts):

        try:

            response = requests.get(message_status_endpoint, headers=headers)

            if response.status_code == 200:

                message_data = response.json()
 
                # Check if the email has been sent

                if "sentDateTime" in message_data:

                    sent_time = message_data["sentDateTime"]

                    logging.info(f"Email was sent at: {sent_time}")

                    return sent_time  # Return the sent timestamp

                else:

                    logging.info(f"Email not sent yet. Checking again in {wait_seconds} seconds.")

            else:

                logging.error(f"Failed to fetch message status. Status: {response.status_code}, Message: {response.text}")
 
        except Exception as e:

            logging.error(f"Error polling message status: {str(e)}")
 
        # Wait before trying again

        time.sleep(wait_seconds)  # Use time.sleep for synchronous functions
 
    logging.error(f"Failed to confirm email was sent after {max_attempts} attempts.")

    return None
 


@api_view(['PUT'])
def send_email_and_update_content(request, pk):
    if request.method == 'PUT':
        try:
            # Step 1: Get the EmailContent object based on the provided 'pk'
            email_content = get_object_or_404(Email_Content, pk=pk)
            # Step 2: Parse the request data
            data = json.loads(request.body)
            # Extract the necessary details from the request
            sender_email_id = data.get('sender')
            message_id = data.get('mail_messageId')
            #print(f"Message ID: {message_id}")
            subject_line = data.get('subject')
            dynamic_content = data.get('response')  # AI-generated or custom response
            print(dynamic_content)
            print(sender_email_id)
            print(message_id)
            print(subject_line)
            # Get credentials and other information for sending email (replace with actual credentials)
            client_id = ""  # Add your client ID
            client_secret = ""  # Add your client secret
            tenant_id = ""  # Add your tenant ID
            email_id = ""  # Add your email ID
            microsoft_endpoint = 'https://graph.microsoft.com'

            # Step 3: Get access token
            access_token = get_access_token(client_id, client_secret, tenant_id)

            if not access_token:
                logging.error("Failed to get access token.")
                return Response({"error": "Access token error."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 4: Send the reply email to the unregistered user using Microsoft Graph API
            new_message_id = send_reply_to_unregistered_sender(
                email_id, 
                message_id, 
                microsoft_endpoint, 
                access_token, 
                sender_email_id, 
                subject_line, 
                dynamic_content
            )

            if not new_message_id:
                logging.error("Failed to queue the email.")
                return Response({"error": "Failed to queue email."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 5: Poll to check if the email was sent successfully
            mail_sent_timestamp = poll_message_status(email_id, new_message_id, microsoft_endpoint, access_token)

            if not mail_sent_timestamp:
                logging.error("Failed to confirm email was sent.")
                return Response({"error": "Failed to confirm email sent."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 6: Update the email content in the database
            email_content.response = dynamic_content
            email_content.status = "1"  # Assuming "1" means success
            email_content.mail_sent_timestamp = timezone.now()

            # Save the updated content
            serializer = EmailContentUpdateSerializer(email_content, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                logging.info(f"Email sent at: {mail_sent_timestamp}")

                # Return a successful response
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Email_Content.DoesNotExist:
            return Response({'error': 'Email content not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

