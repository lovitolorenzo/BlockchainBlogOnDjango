from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import User, Post, User_Ip
from .forms import PostForm, CreateUserForm, UserIpForm
from web3 import Web3
import logging

import re

# Create your views here.


logger = logging.getLogger('django')



def on_blockchain():
    posts = Post.objects.filter(on_blockchain=False)
    for post in posts:
        author = str(post.author)
        title = str(post.title)
        text = str(post.text)
        created_date = str(post.created_date)
        data = {f"{author}, {title}, {text}, {created_date}"}
        manage_transaction(str(data), post.id)



def manage_transaction(data, post):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    nonce = web3.eth.getTransactionCount(address)
    gasPrice = web3.eth.gasPrice
    tx = {
        'nonce': nonce,
        'to': '0x0000000000000000000000000000000000000000',
        'value': web3.toWei(0, 'ether'),
        'gas': 100000,
        'gasPrice': gasPrice,
        'data': data.encode('utf-8')
    }
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    relevant_post = Post.objects.get(id=post)
    transaction_id = web3.toHex(tx_hash)
    relevant_post.transaction_id = transaction_id
    relevant_post.on_blockchain = True
    relevant_post.save()
 


def transaction_verification(request):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    posts = Post.objects.all()
    data = []
    for post in posts:
        transaction = post.transaction_id
        data.append(web3.eth.getTransaction(transaction))
    return HttpResponse(data)



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def store_ip(request, user, ip):
    logger.debug('I\'m trying to store the ip! ' + str(ip) )
    form = UserIpForm(request.POST)
    logger.debug(form.errors)
    if form.is_valid():
        logger.debug('Form is valid...' )
        #user_ip = User_Ip()  #form.save(commit=False)
        user_ip = form.save(commit=False)
        user_ip.user = user
        user_ip.ip_address = ip
        user_ip.save()
    else:
        logger.debug('Form is not valid...' )



def manage_ip(request, user, ip):
    # check if the USER has already accessed the BLOG.
    query_user = User_Ip.objects.filter(user=user)
    # If NOT, store the USER with its first IP
    if len(query_user) <= 0 :
        store_ip(request, user, ip)
        return "It's the first time you access the blog. This is your first IP : " + str(ip) + "."
    # else, check if the new IP has already been used to access the blog
    else:
        query_ip = User_Ip.objects.filter(user=request.user).filter(ip_address=ip)
        # IF the IP has already been used, it will be in the DB ----> the IP is RIGHT
        if len(query_ip) == 1 :
            return "You have accessed the blog with the IP : " + str(ip) + ", already stored"
        # ELSE, the USER is accessing the blog with a new IP ----> store it, but notify it via message
        else:
            store_ip(request, user, ip)
            return "You have never accessed the blog with the IP : " + str(ip) + ", pay attention!"



def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip = get_client_ip(request)
        user = authenticate(request,username=username, password=password)
        if user is not None:
            logger.debug('Before LOGIN!')
            login(request, user)
            logger.debug('After LOGIN!')
            message = manage_ip(request, user, ip)
            messages.info(request,message)
            return redirect('home')
        else:
            messages.info(request,'Username or password is incorrect')
    context = {}
    return render(request, 'account/login.html', context)



@login_required(login_url='login')
def post_new(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            censorship_hack(post)
            post.save()

            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'account/post_edit.html', {'form':form})



@login_required(login_url='login')
def post_edit(request, pk):
	post = Post.objects.get(pk=pk)
	if request.method == "POST":
		form = PostForm(request.POST, request.FILES or None, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			censorship_hack(post)
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'account/post_edit.html', {'form': form})



def censorship_hack(p):
	insensitive_hack = re.compile(re.escape('hack'), re.IGNORECASE)
	title = p.title
	text = p.text
	if matching(title, "hack"):
		p.title = insensitive_hack.sub('****', title)
	if matching(text, "hack"):
		p.text = insensitive_hack.sub('****', text)



def success(request):
    return HttpResponse('successfully uploaded')



@login_required(login_url='login')
def post_detail(request, pk):
    on_blockchain()
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'account/post_detail.html', {'post':post})


@login_required(login_url='login')
def user_data(request, pk):
    user_id = request.user.pk
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        form = CreateUserForm(instance=user)
        return render(request, 'account/user_data.html', {'user': user, 'form' : form})
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            logger.debug("my form is valid")
            #user = form.save(commit = False)
            #user.clean_avatar()
            user.save()
            return redirect('user_data', pk=user.pk)
        else:
            logger.debug("my form is not valid")
            form = CreateUserForm(instance=user)
    return redirect('user_data', pk=user.pk)



@login_required(login_url='login')
def user_posts(request, pk):
    posts = Post.objects.filter(author=request.user).order_by('published_date')
    on_blockchain()
    context = pagination(request, posts)
    return render(request, 'account/user_posts.html', {'posts': context})



def registerPage(request):
    form_user = CreateUserForm()
    if request.method == 'POST':
        form_user = CreateUserForm(request.POST)
        if form_user.is_valid():
            form_user.save()
            user = form_user.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user )
            return redirect('login')
    context = {'form': form_user}
    return render(request, 'account/register.html', context)



@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('/login')



@login_required(login_url='login')
def contact(request):
    return render(request, 'account/contact.html', {})


#switch with dictionary
@login_required(login_url='login')
def home(request):
	if request.method == "GET":
		value = request.GET.get('demux','')
	elif request.method == "POST":
		value = request.POST.get('demux','')
	options = {"validate" : search_hack, "filter" : filter, "search_words" : search_words, "" : home_base}
	return options[value](request)

	#re.match(value,'\b(?<!\.)\d+(?!\.)\b') : pagination


def home_base(request):
    posts_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    on_blockchain()
    posts = pagination(request, posts_list)
    return render(request, 'account/home.html', { 'posts': posts })



def pagination(request, posts_list):
	page = request.GET.get('page', 1)
	paginator = Paginator(posts_list, 4)
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	return posts



def filter(request):
	name = request.GET.get('name')
	user = User.objects.filter(username=name).values_list('id', flat=True)
	posts_list = Post.objects.filter(author=user[0]).order_by('published_date')
	posts = pagination(request, posts_list)
	return render(request, 'account/home.html', {'posts': posts})



def search_words(request):
	word = request.GET.get('word')
	posts_list = Post.objects.all()
	w_posts = []
	for p in posts_list:
		title = p.title
		text = p.text
		if matching(title, word) | matching(text, word):
			w_posts.append(p)
	#return HttpResponse(fposts, content_type="application/json")
	posts = pagination(request, w_posts)
	return render(request, 'account/home.html', {'posts': posts})



def search_hack(request):
	insensitive_hack = re.compile(re.escape('hack'), re.IGNORECASE)
	posts_list = Post.objects.all()
	h_posts = []
	for p in posts_list:
		title = p.title
		text = p.text
		if matching(title, "hack"):
			p.title = insensitive_hack.sub('****', title)
			p.save()
			h_posts.append(p)
		if matching(text, "hack"):
			p.text = insensitive_hack.sub('****', text)
			p.save()
			h_posts.append(p)
	posts = pagination(request, h_posts)
	return render(request, 'account/home.html', {'posts': posts})



def matching(words, word):
	for w in words.split():
		if re.match(word, w, re.IGNORECASE):
			return True
	return False



def get_blog_queryset(request, query=None):
    queryset = []
    queries = query.split(" " and "  ")
    for q in queries:
        posts = Post.objects.filter(
            Q(title__icontains=q),
            Q(body__icontains=q),
        ).distinct()
        for post in post:
            queryset.append(post)
    return list(set(queryset))



def blog_queryset_view(request):
    context = {}
    query = ""
    if request.GET:
        query = request.GET['q']
        context['query'] = str(query)

    found_posts = sorted(get_blog_queryset(query), key=attrgetter('date_updated'), reverse=True)

    return render(request, 'account/home.html', context)



@staff_member_required
def postcounter(request):
    total_posts = Post.objects.all().count()
    users = User.objects.all().annotate(post_count=Count('post'))
    context = {'users': users, 'total_posts': total_posts}
    return render(request, 'account/postcounter.html', context)



def last_hour_posts(request):
    last_hour = timezone.now() - timezone.timedelta(hours=1)
    posts = list(Post.objects.filter(published_date__gte=last_hour).values_list('id', 'title', 'author', 'published_date').order_by('published_date'))
    #per passare una query in Json renderla prima una "list"
    return JsonResponse(posts, safe=False)





#https://programmer.group/django-paginator-ajax-dynamic-load-paging.html
#https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
#https://www.caktusgroup.com/blog/2018/10/18/filtering-and-pagination-django/
