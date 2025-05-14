from django.urls import path
from .views import email_content_list, email_content_detail,check_user
from .views import update_email_content
from .views import send_email_and_update_content
from .views import secure_view
#from .views import create_manual_email, get_manual_emails,check_user

urlpatterns = [
    path('secure/', secure_view, name='secure_view'),
    path('check_user/',check_user,name='check_user'),
    path('email-contents/', email_content_list, name='email_content_list'),  # List all email contents
    path('email-contents/<int:pk>/', email_content_detail, name='email_content_detail'),  # Retrieve a specific email content by ID
    #path('email-contents/update/<int:pk>/', update_email_content, name='email-content-update'),
    path('email-contents/update/<int:pk>/', send_email_and_update_content, name='email-content-update'),
    #path('manual-emails/', create_manual_email, name='create_manual_email'),  # Endpoint for creating Manual_Email
    #path('manual-emails/list/', get_manual_emails, name='get_manual_emails'),  # GET endpoint
]
