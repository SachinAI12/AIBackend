from rest_framework import serializers
from .models import Email_Content
from .models import Manual_Email

class EmailContentSerializer(serializers.ModelSerializer):
    # Specify the custom format for the datetime field
    date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    confidence = serializers.SerializerMethodField()
    status =  serializers.SerializerMethodField()
    class Meta:
        model = Email_Content
        fields = '__all__' 

    def get_confidence(self, obj):
        """
        Map the decimal confidence value to 'High', 'Medium', or 'Low'.
        """
        confidence = obj.confidence  # Replace `confidence` with the actual field name from your model
        
        if confidence > 0.89:
            return 'High'
        elif confidence >= 0.50:
            return 'Medium'
        else:
            return 'Low'

    def get_status(self, obj):
        """
        Map the status (0 or 1) to 'Email Sent' or 'Not Sent'.
        """
        status = obj.status  # Replace `status` with your actual field name
        
        if status == "1":
            return 'Email Sent'
        elif status == "0":
            return 'Not Sent'
        else:
            return 'Unknown'  # Fallback in case of unexpected status value


class EmailContentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email_Content
        fields = ['status', 'response', 'mail_sent_timestamp']

       
class ManualEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manual_Email
        fields = ['email_content', 'manual_response'] 
