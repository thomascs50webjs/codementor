from django.shortcuts import render
from .models import Query, Favourite, UserTitle, Pen, User, OnboardingResponse, ContactMessage
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
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Profile

@login_required
def upload_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.profile_picture = request.FILES["profile_picture"]
        profile.save()
        return redirect("settings")  # or wherever your settings/profile page is

    return redirect("settings")





from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.http import HttpResponse

User = get_user_model()

def password_reset_from_key(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')

            if new_password and new_password == confirm_password:
                # ✅ Step 1: Set password (hash)
                user.set_password(new_password)

                # ✅ Step 2: Save to DB
                user.save(update_fields=['password'])

                # ✅ Step 3: Keep session valid (optional)
                update_session_auth_hash(request, user)

                return render(request, 'app/password_reset_from_key.html', {
                    'password_changed': True
                })
            else:
                return render(request, 'app/password_reset_from_key.html', {
                    'error': 'Passwords do not match.',
                    'validlink': True
                })

        return render(request, 'app/password_reset_from_key.html', {'validlink': True})

    return render(request, 'app/password_reset_from_key.html', {'validlink': False})
def index(request):
    needs_onboarding = False
    if request.user.is_authenticated:
        needs_onboarding = not OnboardingResponse.objects.filter(user=request.user).exists()
    return render(request, 'app/index.html', {'needs_onboarding': needs_onboarding})



# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             auth_login(request, user)
#             next_url = request.POST.get('next') or request.GET.get('next')
#             from django.urls import reverse
#             if next_url == '/' or next_url == reverse('index'):
#                 return redirect('index')
#             from .models import OnboardingResponse
#             if OnboardingResponse.objects.filter(user=user).exists():
#                 return redirect('main')
#             else:
#                 return redirect('onboarding')
#         else:
#             return render(request, "app/login.html", {
#                 "message": "Invalid username or password."
#             })
#     return render(request, "ap    p/login.html")

# def login_view(request):
#     return redirect(reverse('socialaccount_login', args=['google']))
def login_redirect_view(request):
    """
    Runs after Google login and sends the user to onboarding or main.
    """
    # If they came from a ?next= URL, go there
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    # If onboarding already done → main
    if OnboardingResponse.objects.filter(user=request.user).exists():
        return redirect('main')
    else:
        return redirect('onboarding')
def projects(request):
    search_q = request.GET.get('q', '').strip()
    terms = search_q.split() if search_q else []

    # Only show pens for the current user
    pens = Pen.objects.filter(user=request.user)

    if terms:
        pens = advanced_title_search(pens, search_q)
    pens = pens.order_by('-created_at')
    paginator = Paginator(pens, 9)
    page_number = request.GET.get('page')
    postPage = paginator.get_page(page_number)

    not_found = bool(terms) and not pens.exists()

    has_agreed_policy = False
    if request.user.is_authenticated:
        has_agreed_policy = getattr(request.user, 'has_agreed_policy', False)

    return render(request, "app/projects.html", {
        "postPage": postPage,
        "search_q": search_q,
        "not_found": not_found,
        "has_agreed_policy": has_agreed_policy,
    })


def library(request):
    return render(request, "app/library.html")




def logout_view(request):
    logout(request)
    return redirect('index')


# def register(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]
#         password = request.POST["password"]
#         confirmation = request.POST["confirmation"]
#         if password != confirmation:
#             return render(request, "app/register.html", {
#                 "message": "Passwords must match."
#             })
#         try:
#             user = User.objects.create_user(username, email, password)
#             user.save()
#         except IntegrityError:
#             return render(request, "app/register.html", {
#                 "message": "Username already taken."
#             })
#         login(request, user)
#         return redirect('onboarding')
#     else:
#         return render(request, "app/register.html")
    



def advanced_title_search(queryset, search_q):
    """
    Advanced search: matches if all words in search_q are in the title (in any order),
    or if the search_q is a substring of the title (case-insensitive).
    """
    if not search_q:
        return queryset
    terms = search_q.strip().split()
    q_object = Q()
    # Match if all words are present (in any order)
    for term in terms:
        q_object &= Q(title__icontains=term)
    # Also match if the whole search string is a substring
    q_object |= Q(title__icontains=search_q)
    return queryset.filter(q_object)


def main(request):
    # 1) Read and split the search term
    search_q = request.GET.get('q', '').strip()
    terms = search_q.split() if search_q else []

    # 2) Show all pens from all users (excluding forked pens and edited versions)
    pens = Pen.objects.exclude(title__startswith='Fork of').exclude(title__startswith='Edited by')

    # 3) If they typed anything, build an OR-query
    if terms:
        pens = advanced_title_search(pens, search_q)

    # 4) Order, paginate
    pens = pens.order_by('-created_at')
    paginator = Paginator(pens, 9)
    page_number = request.GET.get('page')
    postPage = paginator.get_page(page_number)

    # 5) "Not found" only if they searched and got zero results
    not_found = bool(terms) and not pens.exists()

    # 6) User's custom dashboard title
    if request.user.is_authenticated:
        obj = UserTitle.objects.filter(user=request.user).first()
        title_text = obj.title if obj else "Untitled"
        has_agreed_policy = getattr(request.user, 'has_agreed_policy', False)
    else:
        title_text = "Untitled"
        has_agreed_policy = False

    return render(request, "app/main.html", {
        "postPage":    postPage,
        "title_text":  title_text,
        "search_q":    search_q,
        "not_found":   not_found,
        "has_agreed_policy": has_agreed_policy,
        'pens': pens,
    })

@login_required
def create(request):
    if not request.user.has_agreed_policy:
        return redirect('policy')

    if request.method == "POST":
        extra_files = {}
        for key, value in request.POST.items():
            if key.endswith("_code") and key not in ["html_code", "css_code", "js_code"]:
                filename = key.replace("_code", "")
                extra_files[filename] = value

        pen = Pen.objects.create(
            user=request.user,
            title=request.POST.get("title", "Untitled"),
            html_code=request.POST.get("html_code", ""),
            css_code=request.POST.get("css_code", ""),
            js_code=request.POST.get("js_code", ""),
            extra_files=extra_files,
            is_draft=True
        )
        return redirect('edit_pen', pen_id=pen.id)

    # If GET request
    if request.GET.get('reset_title') == '1':
        UserTitle.objects.filter(user=request.user).delete()

    Pen.objects.filter(user=request.user, html_code='', css_code='', js_code='').delete()

    pen_obj = Pen.objects.filter(user=request.user, is_draft=True).order_by('-id').first()
    user_title_obj = UserTitle.objects.filter(user=request.user).first()
    title_text = user_title_obj.title if user_title_obj else "Untitled"

    has_code_content = bool(
        pen_obj and (pen_obj.html_code.strip() or pen_obj.css_code.strip() or pen_obj.js_code.strip())
    )

    context = {
        'pen': pen_obj,
        'is_create': True,
        'saved': True,
        'title_text': title_text,
        'has_code_content': has_code_content,
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
            js_code=js,
            is_draft=False  # Mark as not draft so it appears in main.html
        )
        
        # Clear the temporary title and pen object after posting
        UserTitle.objects.filter(user=request.user).delete()  # type: ignore
        Pen.objects.filter(user=request.user, is_draft=True).delete()  # type: ignore
        
        return HttpResponseRedirect(reverse("main") + "?posted=1")
    return HttpResponseRedirect(reverse("main"))



@login_required
def code(request, pen_id):
    pen = get_object_or_404(Pen, id=pen_id)

    if request.method == "POST":
        pen.title = request.POST.get("title", "Untitled")
        pen.html_code = request.POST.get("html_code", "")
        pen.css_code = request.POST.get("css_code", "")
        pen.js_code = request.POST.get("js_code", "")
        return redirect('edit_pen', pen_id=pen.id)

    return render(request, "app/edit.html", {
        "pen": pen,
        "editing": True,
        "is_owner": pen.user == request.user,
        
    })


def save_current_pen(request):
    if request.method == 'POST':
        html = request.POST.get('html_code', '')
        css  = request.POST.get('css_code', '')
        js   = request.POST.get('js_code', '')

        pen = Pen.objects.filter(user=request.user, is_draft=True).order_by('-id').first()  # type: ignore
        if pen:
            pen.html_code = html
            pen.css_code = css
            pen.js_code = js
        else:
            # Create a new draft pen
            pen = Pen(user=request.user, html_code=html, css_code=css, js_code=js, is_draft=True)

        pen.save()

        # Return JSON response for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        # 👇 Redirect to create with ?saved=1 flag for regular requests
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

def onboarding(request):
    # If user already completed onboarding, redirect
    if OnboardingResponse.objects.filter(user=request.user).exists():
        return redirect('main')
    onboarding_data = None
    if request.user.is_authenticated:
        onboarding_data = OnboardingResponse.objects.filter(user=request.user).first()
    if request.method == 'POST':
        q1 = request.POST.get('question_one')
        q2 = request.POST.get('question_two')
        # Save or update onboarding response for this user
        OnboardingResponse.objects.update_or_create(
            user=request.user,
            defaults={'question_one': q1, 'question_two': q2}
        )
        return redirect('main')
    context = {
        'onboarding_data': onboarding_data
    }
    return render(request, 'app/onboarding.html', context)

@csrf_exempt
def onboarding_submit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        answer1 = data.get('answer1')
        answer2 = data.get('answer2')
        if request.user.is_authenticated:
            # Only one onboarding per user (OneToOneField)
            OnboardingResponse.objects.update_or_create(
                user=request.user,
                defaults={
                    'question_one': answer1,
                    'question_two': answer2,
                    'current_step': 2,  # Mark as completed
                }
            )
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def onboarding_auto_save(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        answer1 = data.get('answer1', '')
        answer2 = data.get('answer2', '')
        current_step = data.get('current_step', 1)
        
        if request.user.is_authenticated:
            OnboardingResponse.objects.update_or_create(
                user=request.user,
                defaults={
                    'question_one': answer1,
                    'question_two': answer2,
                }
            )
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)



def help_center(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        ContactMessage.objects.create(
            full_name=full_name,
            subject=subject,
            message=message
        )
        return render(request, 'app/help_center.html', {'success': True})
    return render(request, 'app/help_center.html')

def about(request):
    return render(request, "app/about.html")

@csrf_exempt
def increment_view(request, pen_id):
    """Increment view count for a pen when someone clicks on it."""
    if request.method == 'POST':
        try:
            pen = Pen.objects.get(id=pen_id)
            pen.views += 1
            pen.save()
            return JsonResponse({'success': True, 'views': pen.views})
        except Pen.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pen not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def profile(request):
    if request.method == "POST":
        new_username = request.POST.get("username", "").strip()
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Username updated successfully!")
    if request.method == "POST" and request.FILES.get("profile_picture"):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.profile_picture = request.FILES["profile_picture"]
        profile.save()
        return redirect("profile")

    # Get user's pens count
    pens_count = Pen.objects.filter(user=request.user).count()
    

    # Get user's recent pens (last 5)
    recent_pens = Pen.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Get user's stats
    total_views = sum(pen.views for pen in Pen.objects.filter(user=request.user)) if hasattr(Pen.objects.first(), 'views') else 0

    has_agreed_policy = getattr(request.user, 'has_agreed_policy', False)

    return render(request, "app/profile.html", {
        "pens_count": pens_count,
        "recent_pens": recent_pens,
        "total_views": total_views,
        "has_agreed_policy": has_agreed_policy,
    })
def settings(request):
    if request.user.is_authenticated:
        pens_count = Pen.objects.filter(user=request.user).count()

        recent_pens = Pen.objects.filter(user=request.user).order_by('-created_at')[:5]
        reedits_count = Pen.objects.filter(
            title__startswith='Edited by',
            user=request.user
        ).count()

        total_views = (
            sum(pen.views for pen in Pen.objects.filter(user=request.user))
            if hasattr(Pen.objects.first(), 'views')
            else 0
        )

        pens = Pen.objects.filter(user=request.user) \
            .exclude(title__startswith='Fork of') \
            .exclude(title__startswith='Edited by') \
            .count()

        has_agreed_policy = getattr(request.user, 'has_agreed_policy', False)
    else:
        pens_count = 0
        recent_pens = []
        reedits_count = 0
        total_views = 0
        pens = 0
        has_agreed_policy = False

    return render(request, "app/settings.html", {
        "pens_count": pens_count,
        "recent_pens": recent_pens,
        "total_views": total_views,
        "has_agreed_policy": has_agreed_policy,
        'abc': reedits_count,
        'pens': pens,
    })
    




@login_required
@csrf_exempt
def policy(request):
    if request.method == 'POST':
        if 'agree' in request.POST:
            request.user.has_agreed_policy = True
            request.user.save()
            return redirect('create')
        elif 'decline' in request.POST:
            return redirect('main')
    return render(request, "app/policy.html")

@login_required
def fork_pen(request, pen_id):
    """Show fork page for an existing pen/template"""
    try:
        original_pen = get_object_or_404(Pen, id=pen_id)
        
        # Don't create a pen yet - just pass the original pen data
        # The pen will only be created when user clicks "Save Fork"
        forked_pen_data = {
            "title": f"Fork of {original_pen.title}",
            "html_code": original_pen.html_code,
            "css_code": original_pen.css_code,
            "js_code": original_pen.js_code,
            "id": None  # No ID yet since fork hasn't been created
        }
        
        return render(request, "app/fork.html", {
            "forked_pen": forked_pen_data,
            "original_pen": original_pen,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@csrf_exempt
def save_fork(request):
    """Save the forked pen - only creates new pen when user clicks Save Fork"""
    if request.method == 'POST':
        try:
            html_code = request.POST.get('html_code', '')
            css_code = request.POST.get('css_code', '')
            js_code = request.POST.get('js_code', '')
            title = request.POST.get('title', 'Forked Template')
            
            # Always create a new pen since we don't create one in fork_pen view
            pen = Pen.objects.create(
                user=request.user,
                title=title,
                html_code=html_code,
                css_code=css_code,
                js_code=js_code,
                is_draft=False,  # Mark as not draft since user saved it
                is_fork=True  # Mark as fork since it's a forked template
            )
            
            return JsonResponse({
                'success': True,
                'pen_id': pen.id,
                'message': 'Fork saved successfully!',
                'redirect_url': '/projects/'  # Redirect to projects page
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def save_edit(request):
    """Save the edited version of user's own template"""
    if request.method == 'POST':
        try:
            html_code = request.POST.get('html_code', '')
            css_code = request.POST.get('css_code', '')
            js_code = request.POST.get('js_code', '')
            title = request.POST.get('title', 'Edited Template')
            original_pen_id = request.POST.get('original_pen_id', None)
            
            # Add "Edited by" prefix to title like fork.html does
            if not title.startswith('Edited by'):
                title = f"Edited by {title}"
            
            if not original_pen_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Original pen ID is required'
                }, status=400)
            
            # Create a new edited version
            pen = Pen.objects.create(
                user=request.user,
                title=title,
                html_code=html_code,
                css_code=css_code,
                js_code=js_code,
                is_draft=True,  # Mark as draft so it appears in projects.html but not main.html
                is_edited=True  # Mark as edited template
            )
            
            return JsonResponse({
                'success': True,
                'pen_id': pen.id,
                'message': 'Template saved successfully!',
                'redirect_url': '/projects/'  # Redirect to projects page
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

from django.views.decorators.http import require_POST

@login_required
def delete_pen(request, pen_id):
    pen = get_object_or_404(Pen, id=pen_id, user=request.user)
    pen.delete()
    return redirect('main')  #


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("settings")  # Replace with your home URL name
    return redirect("index")

def switch_account_view(request):
    
    logout(request)
    return redirect("/accounts/google/login/?prompt=select_account")