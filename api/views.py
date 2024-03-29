from django.shortcuts import render,redirect
from .models import *
from django.views.generic import View
from django.core.mail import send_mail
# Create your views here.

# def Home(request):
#     return render(request,'shop-index.html')

class BaseView(View):
    views = {}

class HomeView(BaseView):
    def get(self,request):
        self.views['categories'] = Category.objects.all()
        self.views['subcategories'] = SubCategory.objects.all()
        self.views['sliders'] = Slider.objects.all()
        self.views['ads'] = Ad.objects.all()
        self.views['products'] = Product.objects.filter(stock = 'In Stock')
        self.views['sale_products'] = Product.objects.filter(labels='sale',stock = 'In Stock')
        self.views['hot_products'] = Product.objects.filter(labels='hot',stock = 'In Stock')
        self.views['new_products'] = Product.objects.filter(labels='new',stock = 'In Stock')

        return render(request,'shop-index.html', self.views)

class DetailView(BaseView):
    def get(self,request,slug):
        self.views['product_detail'] = Product.objects.filter(slug = slug)

        return render(request,'shop-item.html',self.views)

class CategoryView(BaseView):
	def get(self,request,slug):
		cat_id = Category.objects.get(slug = slug).id
		cat_name = Category.objects.get(slug = slug).name
		self.views['cat_name'] = cat_name
		self.views['subcategories'] = SubCategory.objects.filter(category_id = cat_id)
		self.views['category_products'] = Product.objects.filter(category_id = cat_id)
		# self.views['categories'] = Category.objects.filter(slug = slug)


		return render(request,'category.html',self.views)

class SubCategoryView(BaseView):
	def get(self,request,slug):
		subcat_id = SubCategory.objects.get(slug = slug).id
		self.views['subcategory_products'] = Product.objects.filter(subcategory_id = subcat_id)

		return render(request,'subcategory.html',self.views)

from django.db.models import Q

class SearchView(BaseView):
    def get(self,request):
        if request.method == 'GET':
            query = request.GET['query']
            self.views['search_product'] = Product.objects.filter(name__icontains = query)
            # lookups= Q(name__icontains=query) | Q(description__icontains=query)
			# self.views['search_product'] = Product.objects.filter(lookups).distinct()
            self.views['search_for'] = query

        return render(request,'shop-search-result.html',self.views)


from django.contrib import messages
from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        if password == cpassword:
            number = random.sample(range(1000,9999),1)
            if User.objects.filter(username = username).exists():
                messages.error(request,'The username is already taken')
                return redirect('/signup')
            elif User.objects.filter(email = email).exists():
                messages.error(request,'The email is taken')
                return redirect('/signup')
            else:
                user = User.objects.create(
                    username = username,
                    email = email,
                    password = password
                )
                user.save()
                code = OTP.objects.create(
                    user = username,
                    otp = number[0]
                )
                code.save()
                email = EmailMessage(
                'Verfication code is sent',
                f'Enter your verification code {number[0]}',
                '<Your email>',
                ['<Gmail>'],
                )
                email.send()
                messages.error(request,'The otp code is sent to your email')
                return redirect('/verify')

        else:
            messages.error(request,'The password does not match')
            return render(request,'shop-standart-forms.html')

    return render(request,'shop-standart-forms.html')

def verification(request):
    if request.method == "POST":
        code = request.POST["code"]
        username = request.POST["username"]
        if OTP.objects.filter(otp = code, user = username).exists():
            User.objects.filter(username = username).update(is_active = True)
    return render(request,'otp.html')

def cart(request,slug):
    if Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).exists():
        quantity = Cart.objects.get(slug=slug,user=request.user.username,checkout=False).quantity
        quantity = quantity + 1
        Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).update(quantity = quantity)
    else:
        username = request.user.username
        data = Cart.objects.create(
            user = username,
            slug = slug,
            items = Product.objects.filter(slug = slug)[0],
        )
        data.save()

    return redirect('/mycart')

def deletecart(request,slug):
    if Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).exists():
        Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).delete()

    return redirect('/mycart')

def decreasecart(request,slug):
    if Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).exists():
        quantity = Cart.objects.get(slug=slug,user=request.user.username,checkout=False).quantity
        if quantity > 1:
            quantity = quantity - 1
            Cart.objects.filter(slug=slug,user=request.user.username,checkout=False).update(quantity = quantity)

    return redirect('/mycart')

class CartView(BaseView):
    def get(self,request):
        self.views['cart_product'] = Cart.objects.filter(user=request.user.username,checkout=False)

        return render(request,'shop-shopping-cart.html',self.views)

def shopwhish(request):
    return render(request,'shop-wishlist.html')
# class WishListView(BaseView):
#     def get(self,request):
#         self.views['product_detail'] = Product.objects.filter(slug = slug)
#
#         return render(request,'shop-wishlist.html',self.views)


# -------------------API SECTION ------------------------------------
from rest_framework import serializers, viewsets
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter,SearchFilter
from rest_framework import generics

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductFilterViewSet(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["id","name","price","labels","category","subcategory"]
    ordering_fields = ["price","id","name"]
    search_fields = ["name","description","slug"]

from rest_framework.response import Response
from rest_framework.views import APIView

class ProductCRUDViewSet(APIView):
    def get_object(self,pk):
        try:
            return Product.objects.get(pk=pk)
        except:
            print("The id is not in the DB")
    def get(self,request,pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def post(self,request,pk):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk):
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
