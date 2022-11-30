from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from .forms import CheckoutForm, PaymentForm,  UpdateUserForm, UpdateShippingAddressForm, OpinionCreateForm, ResponseCreateForm, ShippingMethodForm
from .models import Item, OrderItem, Order, Address, Payment, UserProfile, Opinion, Response
from django.db.models import Q
from django.contrib.auth.models import User
from django_countries.fields import Country

import random
import string
import stripe
stripe.api_key = 'sk_test_51M8N83LUQcNgnuxJ2XXhoqtj8ZuXggd9j8afnEAcm3MsmveoH3GooDxNE5gIygJ6RtfcLllQ0s8gghb42VYypeyh00oFdKLhAM'


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def allProducts(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "filter.html", context)

def products_selected(request):
    context = {
        'object_list': Item.objects.filter(selected=True)
    }
    messages.info(request, "Aviso de privacidad: Este sitio no utiliza cookies, no registraremos tus datos")
    return render(request, "home.html", context)

def getProductsByCategories(request,category):
    queryset = request.GET.get("search")
    products = Item.objects.filter(category=category)
    if queryset:
        products = Item.objects.filter(
            Q(title__icontains = queryset)
        ).distinct
    context = {
        'object_list': products 
    }
    return render(request, "home.html", context)


def getOrderByRefCode(request):
    queryset = request.GET.get("ref_code")
    orders = Order.objects.filter(ref_code = queryset)
    context = {
        'orders': orders
    }
    return render(request, "ordersByUser.html", context)

def products(request):
    queryset = request.GET.get("search")
    products = Item.objects.all()
    if queryset:
        products = Item.objects.filter(
           Q(title__icontains = queryset)
        ).distinct
    context = {
        'object_list': products
    }
    return render(request, "home.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

@login_required
def profile(request):
    usuario = request.user
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=usuario)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'El perfil ha sido actualizado con éxito')
            return  render(request, 'profile.html', {'user_form': user_form})
    else:
        user_form = UpdateUserForm(instance=usuario)
    return render(request, 'profile.html', {'user_form': user_form})

@login_required
def user_orders(request):
    user = request.user
    context = {
        'orders' : Order.objects.filter(ordered = True,user=user)
    }       
    return render(request,'ordersByUser.html', context)
    
    
 
def update_shipping_address(request, order_id):
    if request.method == 'POST':
        shipping_form = UpdateShippingAddressForm(request.POST)
        
        if shipping_form.is_valid():
            try:
                shipping_address = shipping_form.cleaned_data.get('shipping_address')
                order = Order.objects.get(id=order_id)
                shipping_address_model = order.shipping_address
                shipping_address_model.street_address = shipping_address
                shipping_address_model.save()
                order.shipping_address = shipping_address_model
                order.save()

                messages.success(request, 'La dirección de envío ha sido actualizada con éxito')
                return redirect('/user/orders')
            except:
                messages.error(request, 'La dirección no se ha podido modificar')
                return redirect('/user/orders/%s/edit' %(order_id))
    else:
        shipping_form = UpdateShippingAddressForm()
        context = {
            'form' : shipping_form
        }
        return render(request,'updateAddressForm.html',context)


@login_required
def delete_user(request):
    user = request.user
    user.delete()
    messages.success(request, 'El perfil ha sido borrado con éxito')
    return redirect('/', foo='bar')

class CheckoutView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        try:
            order = Order.objects.get(user=usuario, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order
            }

            shipping_address_qs = Address.objects.filter(
                user=usuario,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=usuario,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "No puedes realizar la acción seleccionada, no esta activa")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=usuario, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Usando dirección de facturación por defecto")
                    address_qs = Address.objects.filter(
                        user=usuario,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No existe dirección de envío por")
                        return redirect('core:checkout')
                else:
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=usuario,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Por favor, completa los datos de la dirección de envío")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Usando la dirección de facturación por defecto")
                    address_qs = Address.objects.filter(
                        user=usuario,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No existe dirección de facturación por defecto")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=usuario,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Por favor, rellena los datos de facturación")
                        return redirect('core:checkout')

                payment_option = form.cleaned_data.get('payment_option')
                email = form.cleaned_data.get('email')
                order.email = email
                if payment_option == 'S':
                    order.payment_type = False
                    order.save()
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'C':
                    order.payment_type = True
                    order.save()
                    return redirect('core:payment', payment_option='Contrareembolso')
                else:
                    messages.warning(
                        self.request, "Opción de pago seleccionada incorrecta")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "No puedes realizar la acción seleccionada, no está activa")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        order = Order.objects.get(user=usuario, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'payment_option': order.payment_type
            }
            userprofile = usuario.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "No has añadido dirección de facturación")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        order = Order.objects.get(user=usuario, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=usuario)
        if form.is_valid():
            if order.payment_type:
                try:
                    payment = Payment()
                    payment.user = usuario
                    payment.amount = order.get_total()
                    payment.save()

                    # assign the payment to the order

                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()
                    email = order.email
                    print(email)

                    template = get_template('email-order-success.html')

                    # Se renderiza el template y se envias parametros
                    content = template.render({'email': email,'order': order})

                    # Se crea el correo (titulo, mensaje, emisor, destinatario)
                    msg = EmailMultiAlternatives(
                        'Gracias por tu compra',
                        'Hola, te enviamos un correo con tu factura',
                        settings.EMAIL_HOST_USER,
                        [email]
                    )

                    msg.attach_alternative(content, 'text/html')
                    msg.send()
                    messages.success(self.request, "Tu pedido fue un exito! Recibirás un correo con los datos del envío, tu número de referencia del pedido es " + order.ref_code)
                    return redirect("/")
                except Exception as e:
                    # send an email to ourselves
                    messages.warning(
                        self.request, "Ha ocurrido un problema grave. Hemos registado la incidencia")
                    return redirect("/")
            else:
                token = form.cleaned_data.get('stripeToken')
                save = form.cleaned_data.get('save')
                use_default = form.cleaned_data.get('use_default')

                if save:
                    if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                        customer = stripe.Customer.retrieve(
                            userprofile.stripe_customer_id)
                        customer.sources.create(source=token)

                    else:
                        customer = stripe.Customer.create(
                            email=usuario.email,
                        )
                        customer.sources.create(source=token)
                        userprofile.stripe_customer_id = customer['id']
                        userprofile.one_click_purchasing = True
                        userprofile.save()

                amount = int(order.get_total() * 100)

                try:

                    if use_default or save:
                        # charge the customer because we cannot charge the token more than once
                        charge = stripe.Charge.create(
                            amount=amount,  # cents
                            currency="usd",
                            customer=userprofile.stripe_customer_id
                        )
                    else:
                        # charge once off on the token
                        charge = stripe.Charge.create(
                            amount=amount,  # cents
                            currency="usd",
                            source=token
                        )

                    # create the payment
                    payment = Payment()
                    payment.stripe_charge_id = charge['id']
                    payment.user = usuario
                    payment.amount = order.get_total()
                    payment.save()

                    # assign the payment to the order

                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()

                    email = order.email
                    print(email)

                    template = get_template('email-order-success.html')

                    # Se renderiza el template y se envias parametros
                    content = template.render({'email': email,'order': order})

                    # Se crea el correo (titulo, mensaje, emisor, destinatario)
                    msg = EmailMultiAlternatives(
                        'Gracias por tu compra',
                        'Hola, te enviamos un correo con tu factura',
                        settings.EMAIL_HOST_USER,
                        [email]
                    )

                    msg.attach_alternative(content, 'text/html')
                    msg.send()
                    messages.success(self.request, "Tu pedido fue un exito! Recibirás un correo con los datos del envío, tu número de referencia del pedido es " + order.ref_code)
                    return redirect("/")

                except stripe.error.CardError as e:
                    body = e.json_body
                    err = body.get('error', {})
                    messages.warning(self.request, f"{err.get('message')}")
                    return redirect("/")

                except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    messages.warning(self.request, "Rate limit error")
                    return redirect("/")

                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    print(e)
                    messages.warning(self.request, "Invalid parameters")
                    return redirect("/")

                except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    messages.warning(self.request, "Not authenticated")
                    return redirect("/")

                except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    messages.warning(self.request, "Network error")
                    return redirect("/")

                except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    messages.warning(
                        self.request, "Algo ha ido mal, no se le ha cobrado. Por favor inténtelo de nuevo")
                    return redirect("/")

                except Exception as e:
                    # send an email to ourselves
                    messages.warning(
                        self.request, "Ha ocurrido un problema grave. Hemos registrado la incidencia ")
                    return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = Item
    paginate_by = 12
    template_name = "home.html"


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        try:
            form = ShippingMethodForm()
            order = Order.objects.get(user=usuario, ordered=False)
            context = {
                    'object': order,
                    'form':form
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "No tienes activo la orden")
            return redirect("/")

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            usuario = self.request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        form = ShippingMethodForm(self.request.POST or None)
        try:
            if form.is_valid:
                order = Order.objects.get(user = usuario, ordered = False)
                shippingoption = form.cleaned_data.get('shipping_option')
                print(shippingoption)

                order.shipping = shippingoption=='D'
                if not(order.shipping):
                    order.shipping_address = Address.objects.get(id=3)
                order.save()
                return redirect('/checkout/')
        except:
            messages.error(self.request, 'La dirección no se ha podido modificar')
            return redirect('/order-summary/')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def add_to_cart(request, slug):
        if request.user.is_authenticated:
            usuario = request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
  
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=usuario,
            ordered=False
        )
        order_qs = Order.objects.filter(user=usuario, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "El objeto ha sido actualizado.")
                return redirect("core:order-summary")
            else:
                order.items.add(order_item)
                messages.info(request, "El objeto ha sido añadido a tu carrito")
                return redirect("core:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=usuario, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "El objeto ya estaba añadido en tu carrito")
            return redirect("core:order-summary")
   


def remove_from_cart(request, slug):
    if request.user.is_authenticated:
            usuario = request.user
    else:
            usuario = User.objects.get(username = 'anonymous')
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=usuario,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=usuario,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "El objeto ha sido borrado de tu carrito")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Este objeto no estaba en tu cesta")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No tienes ningún pedido activo")
        return redirect("core:product", slug=slug)



def remove_single_item_from_cart(request, slug):
    if request.user.is_authenticated:
            usuario = request.user
    else:
            usuario = User.objects.get(username = 'anonymous')
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=usuario,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=usuario,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "La cantidad del producto ha sido modificada.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "El producto no se encuentra en el carrito")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No tienes activa la orden")
        return redirect("core:product", slug=slug)
    

    
def condiciones(request):
    context = {}
    return render(request, "condiciones.html", context)
    
def politica(request):
    context = {}
    return render(request, "politica.html", context)

@login_required
def opinions(request):
    context = {
        'opinions' : Opinion.objects.all()
    }       
    return render(request,'opinions2.html', context)


@login_required
def opinions_details(request, opinion_id):
    opinion = Opinion.objects.get(id = opinion_id)
    responses = Response.objects.filter(opinion = opinion)
    context = {
        'opinion' : opinion,
        'responses' : responses
    }       
    return render(request,'opinionDetails.html', context)

@login_required
def create_opinion(request):
    if request.method == 'POST':
        opinion_form = OpinionCreateForm(request.POST)
        if opinion_form.is_valid():
            try:
                title = opinion_form.cleaned_data.get('title')
                description = opinion_form.cleaned_data.get('description')
                user = request.user
                opinion = Opinion(title = title, description = description, user = user)
                opinion.save()
                messages.success(request, 'La opinión fue añadida con éxito')
                return redirect('/opinions/')
            except:
                messages.error(request, 'La opinión no se ha podido añadir')
                return redirect('/opinions/create')
    else:
        opinion_form = OpinionCreateForm()
        context = {
            'form' : opinion_form
        }
        return render(request,'createOpinion.html',context)


@login_required
def createResponse(request, opinion_id):
    if request.method == 'POST':
        response_form = ResponseCreateForm(request.POST)
        
        if response_form.is_valid():
            try:
                description = response_form.cleaned_data.get('description')
                user = request.user
                opinion = Opinion.objects.get(id=opinion_id)
                response = Response(description = description, user = user,opinion=opinion)
                response.save()
                messages.success(request, 'La respuesta se ha añadido correctamente')
                return redirect('/opinions/%s/' %(opinion_id))
            except:
                messages.error(request, 'La creación de la respuesta ha fallado')
                return redirect('/opinions/%s/addResponse' %(opinion_id))
    else:
        response_form = ResponseCreateForm()
        context = {
            'form' : response_form
        }
        return render(request,'createResponse.html',context)


class Send(View):
    def get(self, request):
        return render(request, 'send.html')
    
    def post(self, request):
        email = request.POST.get('email')
        print(email)

        template = get_template('email-order-success.html')

        # Se renderiza el template y se envias parametros
        content = template.render({'email': email})

        # Se crea el correo (titulo, mensaje, emisor, destinatario)
        msg = EmailMultiAlternatives(
            'Gracias por tu compra',
            'Hola, te enviamos un correo con tu factura',
            settings.EMAIL_HOST_USER,
            [email]
        )

        msg.attach_alternative(content, 'text/html')
        msg.send()

        return render(request, 'send.html')


    def delete_carrito(request):
        if request.user.is_authenticated:
            usuario = request.user
        else:
            usuario = User.objects.get(username = 'anonymous')
        user = usuario
        user.delete()
        messages.success(request, 'El perfil ha sido borrado con éxito')
        return redirect('/', foo='bar')
