from django.db import models
# Create your models here.

class Email_Content(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing primary key
    date = models.DateTimeField()  # Datetime field
    sender = models.CharField(max_length=255)  # Sender's email
    subject = models.CharField(max_length=255)  # Email subject
    senderContent = models.CharField(max_length=255)  # Content from the sender
    status = models.CharField(max_length=255, null=True, blank=True) 
    response = models.TextField()  # Response content (long text)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)  # Confidence score
    mail_sent_timestamp = models.DateTimeField(auto_now_add=True, null=True) # manual mail sent timestamp
    mail_messageId = models.CharField(max_length=255, null=True) #while replying mail unique message id 
    
    class Meta:
        db_table = 'Email_Content'  # Specify the exact table name if needed

    def __str__(self):
        return f"{self.subject} from {self.sender} on {self.date}"

class Manual_Email(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing primary key
    email_content = models.ForeignKey(Email_Content, on_delete=models.CASCADE)  # Foreign key relationship
    manual_response = models.TextField()  # Use TextField for LONGTEXT
    send_time = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when created

    class Meta:
        db_table = 'Manual_Email'  # Specify the exact table name if needed

    def __str__(self):
        return f"Manual response for Email ID: {self.email_content.id} at {self.send_time}"



from django.db import models
from django.utils import timezone
class LoginUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'login_user'  # Maps to the MySQL table we created

    def __str__(self):
        return self.email
