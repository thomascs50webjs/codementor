from django.shortcuts import render
from .models import Query, Favourite, UserTitle, Pen, User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.contrib.auth import authenticate, login as auth_login
from django.db.models import Q
from typing import Optional




def index(request):
    return render(request, 'app/index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            return render(request, "app/login.html", {
                "message": "Invalid username or password."
            })
    return render(request, "app/login.html")

def projects(request):
    project = Pen.objects.filter(user=request.user).order_by('-created_at')  # type: ignore
    paginatorPro    = Paginator(project, 9)
    page_number  = request.GET.get('page')
    postPagePro     = paginatorPro.get_page(page_number)
    return render(request, "app/projects.html", {"postPagePro": postPagePro})




def logout_view(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")
    



def main(request):
    # 1) Read and split the search term
    search_q = request.GET.get('q', '').strip()
    terms    = search_q.split() if search_q else []

    # 2) Start with this user's pens
    pens = Pen.objects.filter(user=request.user)  # type: ignore

    # 3) If they typed anything, build an OR‑query:
    if terms:
        q_object = Q()
        for term in terms:
            # add a clause: title contains this term
            q_object |= Q(title__icontains=term)  # type: ignore
        pens = pens.filter(q_object)

    # 4) Order, paginate
    pens = pens.order_by('-created_at')
    paginator   = Paginator(pens, 6)
    page_number = request.GET.get('page')
    postPage    = paginator.get_page(page_number)

    # 5) "Not found" only if they searched and got zero results
    not_found = bool(terms) and not pens.exists()

    # 6) User's custom dashboard title
    obj        = UserTitle.objects.filter(user=request.user).first()  # type: ignore
    title_text = obj.title if obj else "Untitled"

    return render(request, "app/main.html", {
        "postPage":    postPage,
        "title_text":  title_text,
        "search_q":    search_q,
        "not_found":   not_found,
    })

def create(request):
    # If user clicked "Create New Pen" with ?reset_title=1, delete any saved title
    if request.GET.get('reset_title') == '1':
        UserTitle.objects.filter(user=request.user).delete()  # type: ignore

    pen_obj = Pen.objects.filter(user=request.user).order_by('-id').first()  # type: ignore
    user_title_obj = UserTitle.objects.filter(user=request.user).first()  # type: ignore
    title_text = user_title_obj.title if user_title_obj else "Untitled"

    if not pen_obj:
        pen_obj = Pen.objects.create(user=request.user, html_code='', css_code='', js_code='')  # type: ignore

    context = {
        'pen': pen_obj,
        'is_create': True,
        'saved': True,
        'title_text': title_text,
        'url_main': reverse('main'),
        'url_create': reverse('create'),
        'url_Title': reverse('saved'),
    }
    return render(request, 'app/create.html', context)

def base(request):
    return render(request, "app/base.html")

def saved(request):
    # Only accept AJAX POST s here
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        new_title = request.POST.get('title', '').strip()
        obj, _ = UserTitle.objects.get_or_create(user=request.user)  # type: ignore
        obj.title = new_title
        obj.save()
        return JsonResponse({'title': new_title})
    return JsonResponse({'error': 'Bad request'}, status=400)

def pen(request):
    if request.method == "POST":
        html = request.POST.get("html_code", "")    
        css  = request.POST.get("css_code", "")
        js   = request.POST.get("js_code", "")
        title = request.POST.get("title", "Untitled")
        Pen.objects.create(  # type: ignore
            user=request.user,
            title=title,
            html_code=html,
            css_code=css,
            js_code=js
        )
        return HttpResponseRedirect(reverse("main") + "?posted=1")
    return HttpResponseRedirect(reverse("main"))



def code(request, pen_id):
    pen = get_object_or_404(Pen, id=pen_id)
    if request.method == "POST":
        pen.title = request.POST.get("title", pen.title)
        pen.html_code = request.POST.get("html_code", pen.html_code)
        pen.css_code = request.POST.get("css_code", pen.css_code)
        pen.js_code = request.POST.get("js_code", pen.js_code)
        pen.save()
        return redirect('main')

    return render(request, "app/edit.html", {
        "pen": pen,
        "editing": True,
    })
    
def save_current_pen(request):
    if request.method == 'POST':
        html = request.POST.get('html_code', '')
        css  = request.POST.get('css_code', '')
        js   = request.POST.get('js_code', '')

        pen = Pen.objects.filter(user=request.user).order_by('-id').first()  # type: ignore
        if pen:
            pen.html_code = html
            pen.css_code = css
            pen.js_code = js
        else:
            pen = Pen(user=request.user, html_code=html, css_code=css, js_code=js)

        pen.save()

        # 👇 Redirect to create with ?saved=1 flag
        return redirect(reverse("create") + "?saved=1")

    return redirect('create')

def save_pen_title(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            obj, created = UserTitle.objects.get_or_create(user=request.user)  # type: ignore
            obj.title = title
            obj.save()
            return JsonResponse({'success': True, 'title': title})
        return JsonResponse({'success': False, 'error': 'Title cannot be empty'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



