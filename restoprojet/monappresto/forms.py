from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from .models import TableBooking, Order, ContactMessage

class TableBookingForm(forms.ModelForm):
    class Meta:
        model = TableBooking
        fields = ['first_name', 'last_name', 'email', 'phone', 'people', 'booking_date', 'special_requests', 'subscribe_to_newsletter']
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if not booking_date:
            return booking_date
        
        now = timezone.now()
        
        # Booking must be at least 1 hour in advance
        if booking_date < now + timedelta(hours=1):
            raise forms.ValidationError("Booking must be at least 1 hour in advance.")
        
        # Booking can't be more than 30 days in advance
        if booking_date > now + timedelta(days=30):
            raise forms.ValidationError("Booking can't be more than 30 days in advance.")
        
        return booking_date

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['phone', 'email']