from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView,View
from .models import Item,OrderItem,Order,Address,Payment,Cupon,Refund
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
''' if you want login required in for a class '''
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import CheckoutForm,CuponForm,RefundForm,SearchForm
from django.core.exceptions import ObjectDoesNotExist
''' if you want login required in for a funtion'''
from django.contrib.auth.decorators import login_required
import stripe
import random
import string
import smtplib



''' this is stripe key  for stripe payment handle'''
stripe.api_key = settings.STRIPE_KEY


''' create a refund code which length minimum is 20 '''
def create_ref_code ():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20 ))




class Home(ListView):
    model = Item
    template_name = 'index.html'
    paginate_by = 9




def search_item(request):
    try: 
        form = SearchForm(request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            items = Item.objects.filter(title__icontains=search)
            context = {
                'all_search_results':items
            }
            return render(request,"search.html",context)
        else : 
            messages.info(request,"this is not a valid form")
            return redirect('/')
    except ObjectDoesNotExist:
        messages.info(request,"sorry item not found !")
        return redirect('/')


# class SearchView(ListView):
#     model = Item
#     template_name = 'search.html'
#     context_object_name = 'all_search_results'

#     def get_queryset(self):
#         form = SearchForm(self.request.GET or No)
#         result = super(SearchView, self).get_queryset()
#         if form.is_valid():
#             # query = self.request.GET.get('search')
#             query = form.cleaned_data.get('search')

#         if query:
#             print("if condition is working ")
#             postresult = Item.objects.filter(title__icontains=query)
#             result = postresult
#         else:
#             print('esle condition is working')
#             result = None
#         return result
            


        

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'
        

@login_required
def add_cart(requset,slug):
    item = get_object_or_404(Item,slug=slug)
    ''' we need to create if you don't then we don't get the item in OrderItem'''
    order_item ,created = OrderItem.objects.get_or_create(
        item = item,
        user = requset.user,
        ordered = False
    )

    order_qs = Order.objects.filter(
        user = requset.user,
        ordered =False
    )

    if order_qs.exists():
        order = order_qs[0]
        
        if order.items.filter(item__slug = slug).exists():
            order_item.quantity +=1
            order_item.save()
            order.ref_code =create_ref_code()
            messages.success(requset,"your item quantity successfully updated")
            return redirect('core:detailed_summary')
        else:
            order.items.add(order_item)
            messages.success(requset,"your quantity successfully added")
            return redirect('core:detailed_summary')
    else:
        ordered_date = timezone.now()
        ref_code = create_ref_code()
        order = Order.objects.create(user = requset.user,ref_code= ref_code, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.success(requset,"your quantity successfully added")
        return redirect('core:detailed_summary')


        


        
@login_required
def remove_one_cart(requset,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item = OrderItem.objects.filter(
    item= item ,
    user=requset.user,
    ordered=False)

    order_qs = Order.objects.filter(
        user= requset.user,
        ordered = False
    )

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug = slug).exists():
            order_item = order.items.filter(
                item= item,
                user = requset.user,
                ordered = False
            )[0]
            if order_item.quantity  <= 1:
                order.items.remove(order_item)
                messages.info(requset,'your item successfully removed')
                return redirect('/')
            else:
                order_item.quantity -=1
                order_item.save()
                messages.info(requset,'your item quantity successfully updated')
                return redirect('core:detailed_summary')
        else:
            messages.info(requset,"you dont have any active order")
            return redirect('/')
        
    else:
        messages.info(requset,"you dont have any active order")
        return redirect('/')


@login_required
def remove_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False
    )

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug= slug).exists():
            order_item = order.items.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            order_item.save()
            order.items.remove(order_item)
            order_item.quantity = 1
            order_item.save()
            messages.info(request,"your item successfully removed")
            return redirect('core:detailed_summary')
        else:
            messages.info(request,"you don't have any active order")
            return redirect('core:detailed_summary' )
    else:
        messages.info(request,"you don't have any active order")
        return redirect('/')




class DetailedMinxin(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(
                user = self.request.user,
                ordered = False
            )
            context = {
                'order':order
            }
            return render(self.request,'detailed.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request,"you don't have any active order")
            return redirect('/')




def is_valid_form(values):
    valid = True
    for filds in values:
        if filds == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        shipping_address_qs = Address.objects.filter(user= self.request.user ,address_type="S" ,default=True)
        billing_address_qs = Address.objects.filter(user=self.request.user,address_type='B',default=True)

        order = Order.objects.get(user=self.request.user,ordered=False)
        form = CheckoutForm()
        context = {
            'form':form,
            'order' : order
        }

        if order.shipping_address != None:
            if shipping_address_qs.exists():
                context.update({
                    'shipping_address' : shipping_address_qs[0]
                })
        
        if order.billing_address != None:
            if billing_address_qs.exists():
                context.update({
                    'billing_address' : billing_address_qs[0]
                })
            
        
        

        try:
            cupon_list = [ ]
            cupons = Cupon.objects.all()
            index = 0
            for i in range(index,(len(cupons))):
                cupon_qs = Cupon.objects.filter()
                if cupon_qs.exists():
                    cupon = cupon_qs[i]
                    cupon_list.append(cupon)
            context.update({'cupon_list' : cupon_list})
        except ObjectDoesNotExist:
            return render(self.request,'checkout.html',context)
        return render(self.request,'checkout.html',context)
       
   

    def post(self,*args,**kwargs):
        paymetn_method = ''
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm(self.request.POST or None)
        shipping_address_qs = Address.objects.filter(user=self.request.user,address_type='S',default=True)
        billing_address_qs = Address.objects.filter(user=self.request.user,address_type='B',default=True)
        
        print(self.request.POST)
        print(form)
        if form.is_valid():
            # the cleaned_data is a dictonry of user form value and always work after form.is_valid
            payment_method = form.cleaned_data.get('payment_method')

            use_default_shipping = form.cleaned_data.get('shipping_use_default')
            use_default_billing = form.cleaned_data.get('billing_use_default')

            if use_default_shipping:
                if shipping_address_qs.exists():
                    shipping_address = shipping_address_qs[0]
                    shipping_address.save()
                    order.shipping_address = shipping_address
                    order.save()
                    messages.info(self.request,'your default address is submitted')
                    ''' use click billing address same shipping address '''
                    billing_same_as_shipping = form.cleaned_data.get('billing_same_as_shipping')

                if  use_default_billing:
                    billing_address = billing_address_qs[0]
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                    
                    
                if billing_same_as_shipping:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()

                    order.billing_address = billing_address
                    order.save()

                    messages.info(self.request,"you are using billing adress same as shipping address")
                if payment_method == "S":
                    return redirect('core:payment',payment_method = 'stripe')
                elif payment_method == "P":
                    return redirect('core:payment',payment_method = 'paypal')
                else:
                    return messages.info("invalid payment option")
            
         
            else:
                # shipping address
                street_address = form.cleaned_data.get('shipping_street_address')
                apartment_address = form.cleaned_data.get('shipping_apartment_address')
                country = form.cleaned_data.get('shipping_country')
                zip = form.cleaned_data.get('shipping_zip')
                shipping_save_info = form.cleaned_data.get('shipping_save_info')
                billing_save_info = form.cleaned_data.get('billing_save_info')


                if is_valid_form([street_address,apartment_address,country,zip]):
                    shipping_address = Address(
                        user = self.request.user,
                        street_address = street_address,
                        apartment_address = apartment_address,
                        country = country,
                        zip = zip,
                        address_type = 'S'
                    )
                    shipping_address.save()
                    order.shipping_address = shipping_address
                    order.save()

                    if shipping_save_info:
                        shipping_address.default = True
                        shipping_address.save()
                    else:
                        messages.info(self.request,"sorry something went wrong")
                        return redirect('core:checkout')
                        
                    
                    ''' use click billing address same shipping address '''
                    billing_same_as_shipping = form.cleaned_data.get('billing_same_as_shipping')
                    
                    if billing_same_as_shipping:
                        billing_address = shipping_address
                        billing_address.pk = None
                        billing_address.save()
                        billing_address.address_type = 'B'
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        if billing_save_info:
                            billing_address.default = True
                            billing_address.save()


                        messages.info(self.request,"you are using billing adress same as shipping address")
                        if payment_method == "S":
                            return redirect('core:payment',payment_method = 'stripe')
                        elif payment_method == "P":
                            return redirect('core:payment',payment_method = 'paypal')
                        else:
                            return messages.info("invalid payment option")

                    # billing address

                    billing_street_address = form.cleaned_data.get('street_address')
                    billing_apartment_address = form.cleaned_data.get('billing_address')
                    billing_country = form.cleaned_data.get('country')
                    billing_zip = form.cleaned_data.get('zip')


                    billing_address = Address(
                        user = self.request.user,
                        street_address = street_address,
                        apartment_address = apartment_address,
                        country = country,
                        zip = zip,
                    )
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                    messages.success(self.request,'checkout successfully complete')

                    if payment_method == "S":
                        return redirect('core:payment',payment_method = 'stripe')
                    elif payment_method == "P":
                        return redirect('core:payment',payment_method = 'paypal')
                    else:
                        return messages.info("invalid payment option")


                messages.warning(self.request,'not a valid form')
                return redirect('core:checkout')
        messages.warning(self.request,'Faild checkout')
        return redirect('core:checkout')


      
class PaymentView(LoginRequiredMixin,View):
    def get(self, slug, *args,**kwargs):        
        try:
            order = Order.objects.get(user=self.request.user ,ordered=False)
            if order.billing_address != None:
                cupon = Cupon.objects.all()
                context = {
                    'order' : order,
                    'cupon': cupon
                }
                return render(self.request, 'payment.html', context)
            messages.info(self.request,"sorry must add a billing address")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "sorry you don't have any active order")
            return redirect('/')

    def post(self,slug,*args,**kwargs):
        try:
            address_qs  = Address.objects.filter(user=self.request.user)
            order = Order.objects.get(user=self.request.user,ordered=False)
            
            # ''' here we sending a mail to user about order '''
            # ob = smtplib.SMTP('smtp.gmail.com',587)
            # ''' encript connection using  "tls"  using a stmp class fuction  '''
            # ob.starttls() 
            # ob.login('yourid@gmail.com',"your_password")
            # subject  = "Order Successfull on Nsfuntu"
            # body = "your order is successfully you will recive today 12:on clock and your ref id is " + order.ref_code
            # message = "Subject : {}\n\n{}".format(subject,body)
            # sender = 'swaminaresh993@gmail.com'
            # reciver = ['reciver','reciver']
            # ob.sendmail(sender,reciver,message)
            # ob.quit()
            # ''' if success '''
            # messages.success(self.request,'ordered successful')
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_all_product_price()*100)
            charge = stripe.Charge.create(
                amount= amount, # value in cents so i mulitply with 100
                currency='usd',
                source=token
            )   

            # TODO : inserting the payment detail in payment class
            ''' the charge will crete an id and we insert in table usin  " ['id'] " '''
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_all_product_price()
            payment.save() 



            order.ordered = True
            # TODO :  assign the payment in Order 
            order.payment = payment
            order.save()

            # Use Stripe's library to make requests...
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.warning(self.request,f' {e.user_message}')
            return redirect('/')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request,'Too many requests made to the API too quickly')
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request,"Invalid parameters were supplied to Stripe's API")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request,"Authentication with Stripe's API failed")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request,"Network communication with Stripe failed")
            return redirect('/')

        except stripe.error.StripeError as  e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request,"Display a very generic error to the user, and maybe send")
            return redirect('/')
        except ObjectDoesNotExist:
            messages.info(self.request,"you don't have any active order")
            return redirect('/')
        return redirect('/')



        
        

def cupon(request):
    try:
        order = Order.objects.get(user=request.user,ordered=False)
        cupon_form = CuponForm(request.POST or None)
        if cupon_form.is_valid():
            cupon_code = cupon_form.cleaned_data.get('cupon_code')
            cupon = Cupon.objects.get()
            if cupon.cupon_code != cupon_code:
                messages.warning(request,'sorry this is not a valid cupon')
                return redirect('core:chekout')
            order.cupon = cupon
            order.save()
            messages.success(request,'cupon access')
            if order.billing_address.payment_method == "S" and not None:
                return redirect('core:payment',payment_method="stripe" )  
            else :
                return redirect('core:payment' , payment_method="paypal" )  

                
        else: 
            messages.warning(request,'something went wrong')
            return redirect('/')
    except ObjectDoesNotExist:
        messages.info(request,"sorry you don't have any active order")
        return redirect('/')

            
    
                
                

class RefundView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        order_qs  = Order.objects.filter(user=self.request.user,ordered=True, refund_granted=False)
        if order_qs.exists():
            order = order_qs[0]
            form = RefundForm()
            context = {
                'form':form
            }
            return render(self.request,"refund.html",context)
        messages.info(self.request,'first purchase an item for refund !')
        return redirect('/')

    def post(self,*args,**kwargs):
        try:
            form = RefundForm(self.request.POST or None)
            if form.is_valid():
                ref_code = form.cleaned_data.get('ref_code')
                email = form.cleaned_data.get('email')
                resion = form.cleaned_data.get('resion')
                orders = Order.objects.all()
                for order in reversed(orders):
                    if order.refund_requseted == False:
                        if ref_code  == order.ref_code:
                            refund = Refund(
                                user = self.request.user,
                                ref_code = ref_code,
                                order = order,
                                email = email,
                                resion = resion,
                                accepeted = True
                            ).save()
                            order.refund_requseted = True
                            order.save()
                            messages.success(self.request,"your item refund succesfully refunded")
                            return redirect('/')
                    messages.info(self.request , 'your refund request allready submitted')
                    return redirect('/')
                        
            messages.info(self.request,"sorry this is not a valid code !")
            return redirect('/')
        except ObjectDoesNotExist:
            messages.info(self.request,"sorry you don't have any orderd item for refund")
            return redirect('/')




@login_required
def user_dashboard(request):
    try :
        items_list = []
        context = { }
        orders = Order.objects.filter(user=request.user,ordered=True,refund_granted = False)
        context = {
            'orders' : orders
        }
     
        return render(request,'dashbord.html',context)    
    except ObjectDoesNotExist:
        messages.info(request,"must purchase a product for create your dashbord")
        return redirect('/')




            


    