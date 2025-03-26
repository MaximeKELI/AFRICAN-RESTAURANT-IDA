from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import MenuItem, Chef, TableBooking, Order, OrderItem, ContactMessage
from .forms import TableBookingForm, ContactForm, OrderForm

def home(request):
    menu_items = MenuItem.objects.filter(is_available=True)
    chefs = Chef.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'menu_items': menu_items,
        'chefs': chefs,
    })

def about(request):
    return render(request, 'about.html')

def menu(request):
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, 'menu.html', {'menu_items': menu_items})

def chefs(request):
    chefs = Chef.objects.filter(is_active=True)
    return render(request, 'chefs.html', {'chefs': chefs})

@require_http_methods(["GET", "POST"])
def book_table(request):
    if request.method == 'POST':
        form = TableBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Check if the table is available
            existing_bookings = TableBooking.objects.filter(
                booking_date__range=(
                    booking.booking_date - timedelta(hours=2),
                    booking.booking_date + timedelta(hours=2)
                ),
                status__in=['pending', 'confirmed']
            ).count()
            
            if existing_bookings >= 10:  # Assuming 10 is max capacity
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, no available tables at this time. Please try another time.'
                })
            
            booking.save()
            
            # Send confirmation email
            if booking.email:
                send_mail(
                    'Table Booking Confirmation - Ounje Cafe',
                    f'Hello {booking.first_name},\n\n'
                    f'Your table for {booking.people} people has been booked for '
                    f'{booking.booking_date.strftime("%Y-%m-%d %H:%M")}.\n\n'
                    'Thank you for choosing Ounje Cafe!',
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.email],
                    fail_silently=False,
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Table booked successfully!'
                })
            return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = TableBookingForm()
    
    return render(request, 'book_table.html', {'form': form})

@csrf_exempt
@require_http_methods(["POST"])
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'}, status=401)
    
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        menu_item = MenuItem.objects.get(id=item_id, is_available=True)
    except MenuItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
    
    # Get or create an active order for the user
    order, created = Order.objects.get_or_create(
        customer_name=request.user.get_full_name() or request.user.username,
        email=request.user.email,
        phone='',  # User should update this
        status='pending',
        defaults={'total_price': 0}
    )
    
    # Add item to order
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        menu_item=menu_item,
        defaults={
            'quantity': quantity,
            'price_at_order': menu_item.price
        }
    )
    
    if not created:
        order_item.quantity += quantity
        order_item.save()
    
    # Update order total
    order.total_price = sum(
        item.price_at_order * item.quantity 
        for item in order.orderitem_set.all()
    )
    order.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': order.orderitem_set.count(),
        'cart_total': order.total_price
    })

def get_cart_items(request):
    if not request.user.is_authenticated:
        return JsonResponse({'items': [], 'total': 0})
    
    try:
        order = Order.objects.get(
            customer_name=request.user.get_full_name() or request.user.username,
            status='pending'
        )
        items = [{
            'id': item.menu_item.id,
            'name': item.menu_item.name,
            'price': float(item.price_at_order),
            'quantity': item.quantity,
            'image': item.menu_item.image.url if item.menu_item.image else ''
        } for item in order.orderitem_set.all()]
        
        return JsonResponse({
            'items': items,
            'total': float(order.total_price)
        })
    except Order.DoesNotExist:
        return JsonResponse({'items': [], 'total': 0})

@csrf_exempt
@require_http_methods(["POST"])
def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'}, status=401)
    
    item_id = request.POST.get('item_id')
    
    try:
        order = Order.objects.get(
            customer_name=request.user.get_full_name() or request.user.username,
            status='pending'
        )
        order_item = OrderItem.objects.get(
            order=order,
            menu_item_id=item_id
        )
        order_item.delete()
        
        # Update order total
        order.total_price = sum(
            item.price_at_order * item.quantity 
            for item in order.orderitem_set.all()
        )
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_count': order.orderitem_set.count(),
            'cart_total': order.total_price
        })
    except (Order.DoesNotExist, OrderItem.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Item not found in cart'}, status=404)

@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification
            send_mail(
                'New Contact Message - Ounje Cafe',
                f'You have a new message from {contact_message.name} ({contact_message.email}):\n\n'
                f'Subject: {contact_message.subject}\n'
                f'Message: {contact_message.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! We will get back to you soon.'
                })
            return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

@require_http_methods(["GET", "POST"])
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        order = Order.objects.get(
            customer_name=request.user.get_full_name() or request.user.username,
            status='pending'
        )
    except Order.DoesNotExist:
        return redirect('menu')
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'processing'
            order.save()
            
            # Send confirmation email
            if order.email:
                send_mail(
                    'Order Confirmation - Ounje Cafe',
                    f'Hello {order.customer_name},\n\n'
                    f'Your order #{order.id} has been received and is being processed.\n\n'
                    f'Order Total: ${order.total_price}\n\n'
                    'Thank you for choosing Ounje Cafe!',
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False,
                )
            
            return render(request, 'checkout_success.html', {'order': order})
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'checkout.html', {
        'form': form,
        'order': order,
        'order_items': order.orderitem_set.all()
    })