from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
import random
import requests
import stripe
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.http import JsonResponse
# Create your views here.

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

def index(request):
    return render(request,'index.html')

def seller_index(request):
	return render(request,'seller-index.html')

def about(request):
	return render(request,'about.html')

def seller_about(request):
	return render(request,'seller-about.html')

def blog_detail(request):
	return render(request,'blog-detail.html')

def blog(request):
	return render(request,'blog.html')

def contact(request):
	return render(request,'contact.html')

def seller_contact(request):
	return render(request,'seller-contact.html')

def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		try:
			Cart.objects.get(user=user,product=product,payment_status=False)
			cart_flag=True
		except:
			carts=Cart.objects.filter(user=user,product=product,payment_status=True)
			cart_flag=False
	except:
		pass
	return render(request,'product-detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def product(request):
	products=Product.objects.all()
	return render(request,'product.html',{'products':products})

def product_women(request):
	products=Product.objects.filter(product_categories='Women')
	return render(request,'product.html',{'products':products})

def product_women_shirt(request):
	products=Product.objects.filter(product_categories='Women',product_subcategories='Shirt')
	return render(request,'product.html',{'products':products})

def product_women_pant(request):
	products=Product.objects.filter(product_categories='Women',product_subcategories='Pant')
	return render(request,'product.html',{'products':products})

def product_women_shoes(request):
	products=Product.objects.filter(product_categories='Women',product_subcategories='Shoes')
	return render(request,'product.html',{'products':products})

def product_men(request):
	products=Product.objects.filter(product_categories='Men')
	return render(request,'product.html',{'products':products})

def product_men_shirt(request):
	products=Product.objects.filter(product_categories='Men',product_subcategories='Shirt')
	return render(request,'product.html',{'products':products})

def product_men_pant(request):
	products=Product.objects.filter(product_categories='Men',product_subcategories='Pant')
	return render(request,'product.html',{'products':products})

def product_men_shoes(request):
	products=Product.objects.filter(product_categories='Men',product_subcategories='Shoes')
	return render(request,'product.html',{'products':products})

def signup(request):
	if request.method=='POST':
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cnew_password']:
				User.objects.create(
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					adress=request.POST['adress'],
					password=request.POST['password'],
					profile_pic=request.FILES['profile_pic'],
					usertype=request.POST['usertype']
					)
				msg="User SignUp Successfully"
				return render(request,'signup.html',{'msg':msg})
			else:
				msg="Password And Confirm Password Does Not Match"
				return render(request,'signup.html',{'msg':msg})

	else:
		return render(request,'signup.html')

def login(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				request.session['email']=user.email
				request.session['fname']=user.fname
				if user.usertype=='buyer':
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user,payment_status=False)
					request.session['cart_count']=len(carts)
					return render(request,'index.html')
				else:
					return render(request,'seller-index.html')
			else: 
				msg="Incorrect Password"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Registered"
			return render(request,'login.html',{'msg':msg})

	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return redirect('index')
	except:
		return render(request,'login.html')

def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				if user.usertype=='buyer':
					msg="New Password & Confirm New Password Does Not Match"
					return render(request,'change-password.html',{'msg':msg})
				else:
					msg="New Password & Confirm New Password Does Not Match"
					return render(request,'seller-change-password.html',{'msg':msg})
		else:
			if user.usertype=='buyer':
				msg="Entered Password Is Incorrect"
				return render(request,'change-password.html',{'msg':msg})
			else:
				msg="Entered Password Is Incorrect"
				return render(request,'seller-change-password.html',{'msg':msg})

	else:
		if user.usertype=='buyer':
			return render(request,'change-password.html')
		else:
			return render(request,'seller-change-password.html')

def forgot_password(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP For Forgot Password'
			message = "Hello, "+user.fname+" Your OTP For Forgot Password Is "+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':user.email})
		except:
			msg="Your Entered Email Is Not Registered"
			return render(request,'forgot-password.html',{'msg':msg})
	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	email=request.POST['email']
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	if otp==uotp:
		return render(request,'new-password.html',{'email':email})
	else:
		msg="Incorrect OTP"
		return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})

def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']
	if np==cnp:
		user=User.objects.get(email=email)
		user.password=np
		user.save()
		return redirect('login')
	else:
		msg="New Password And Confirm New Password Does Not Matched"
		return render(request,'new-password.html',{'email':email,'msg':msg})


def seller_add_product(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=user,
			product_categories=request.POST['product_categories'],
			product_subcategories=request.POST['product_subcategories'],
			product_name=request.POST['product_name'],
			product_brand=request.POST['product_brand'],
			product_size=request.POST['product_size'],
			product_price=request.POST['product_price'],
			product_description=request.POST['product_description'],
			product_information=request.POST['product_information'],
			product_pic=request.FILES['product_pic']
			)
		msg='Product Added Successfully'
		return render(request,'seller-add-product.html',{'msg':msg})
	else:
		return render(request,'seller-add-product.html')

def seller_view_product(request): 
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user)
	return render(request,'seller-view-product.html',{'products':products})

def seller_women_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Women')
	return render(request,'seller-view-product.html',{'products':products})

def seller_men_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Men')
	return render(request,'seller-view-product.html',{'products':products})

def seller_women_shirt_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Women',product_subcategories='Shirt')
	return render(request,'seller-view-product.html',{'products':products})

def seller_women_pant_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Women',product_subcategories='Pant')
	return render(request,'seller-view-product.html',{'products':products})

def seller_women_shoes_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Women',product_subcategories='Shoes')
	return render(request,'seller-view-product.html',{'products':products})

def seller_men_shirt_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Men',product_subcategories='Shirt')
	return render(request,'seller-view-product.html',{'products':products})

def seller_men_pant_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Men',product_subcategories='Pant')
	return render(request,'seller-view-product.html',{'products':products})

def seller_men_shoes_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user,product_categories='Men',product_subcategories='Shoes')
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-detail.html',{'product':product})

def seller_product_edit(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=='POST':
		product.product_categories=request.POST['product_categories']
		product.product_subcategories=request.POST['product_subcategories']
		product.product_name=request.POST['product_name']
		product.product_brand=request.POST['product_brand']
		product.product_size=request.POST['product_size']
		product.product_price=request.POST['product_price']
		product.product_description=request.POST['product_description']
		product.product_information=request.POST['product_information']

		try:
			product.product_pic=request.FILES['product_pic']
		except:
			pass
		product.save()
		msg="Product Updated Successfully!"
		return render(request,'seller-product-edit.html',{'product':product,'msg':msg})
	else:
		return render(request,'seller-product-edit.html',{'product':product})

def seller_product_delete(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=user)
	msg="Product Deleted Successfully!"
	return render(request,'seller-view-product.html',{'products':products,'msg':msg})

def add_to_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	try:
		cart_product=Cart.objects.get(product=product,user=user,payment_status=False)
		msg="Product Is Already added To Cart!"
		products=Product.objects.all()
		return render(request,'product.html',{'products':products,'msg':msg})
	except:
		try:
			cart_product=Cart.objects.get(product=product,user=user,payment_status=True)
			Wishlist.objects.create(
				user=user,
				product=product
				)
			return redirect('wishlist')
		except:
			Wishlist.objects.create(
				user=user,
				product=product
				)
			return redirect('wishlist')
			
def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def add_to_cart(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	Cart.objects.create(
		user=user,
		product=product,
		product_quantity=1,
		product_price=product.product_price,
		total_price=product.product_price,
		payment_status=False
		)
	try:
		wishlist=Wishlist.objects.get(user=user,product=product)
		wishlist.delete()
	except Wishlist.DoesNotExist:
		pass
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return redirect('shoping-cart')

def shoping_cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price+=i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'shoping-cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('shoping-cart')

def change_quantity(request):
	cid=int(request.POST['cid'])
	product_quantity=int(request.POST['product_quantity'])
	cart=Cart.objects.get(pk=cid)
	cart.product_quantity=product_quantity
	cart.total_price=cart.product_price*product_quantity
	cart.save()
	return redirect('shoping-cart')

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

@csrf_exempt
def create_checkout_session(request):
    amount = int(json.load(request)['post_data'])
    final_amount = amount * 100
    
    try:
        success_url = 'http://cozastoreonline.pythonanywhere.com/success.html'
        cancel_url = 'http://cozastoreonline.pythonanywhere.com/cancel.html'
    except Exception as e:
        print(f"An error occurred while constructing URLs: {e}")
        success_url = YOUR_DOMAIN + '/success.html'
        cancel_url = YOUR_DOMAIN + '/cancel.html'
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': 'Checkout Session Data',
                },
                'unit_amount': final_amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
		
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})

def seller_order(request):
	seller=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(payment_status=True)
	orders=[]
	for i in carts:
		if i.product.seller==seller:
			orders.append(i)
	return render(request,'seller-order.html',{'orders':orders})

