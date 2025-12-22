from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .forms import *
from .filters import *
from .models import *
from django.conf import settings
from django.core.mail import send_mail, mail_admins, BadHeaderError
import logging
import json
import hmac
import hashlib
import os
import uuid
from.utils import validate_signature
import urllib
KASHIER_SECRET = os.environ.get("MID")

logger = logging.getLogger(__name__)
# Create your views here.


def home(request):
    return render(request, "index.html")


def error(request):
    return render(request, "error.html")

def search(request):
    cvs = Website.objects.filter(is_active=True)
    filter = WebsiteFilter(request.GET, queryset = cvs)
    cvs = filter.qs

    context = {
        "cvs" : cvs,
        "filter": filter
    }
    return render(request, "search.html", context)

@login_required
def create(request):
    try:
        website = request.user.profile.website
    except Exception:
        website = None
    if website : return redirect("/") 
    if request.method == "POST":
        form = CreateWebsite(request.POST, request.FILES)
        if form.errors:
            print(form.errors)
        if form.is_valid():
            myform = form.save(commit=False)
            myform.user = request.user.profile
            myform.is_active = False
            myform.save()
            website = Website.objects.get(id=myform.id)
            # certs = request.FILES.getlist("certificates")

            # if certs:
            #     for i in certs:
            #         Certificate.objects.create(cert=i, website=website)
            #     for i in range(4):
            #         skill = request.POST[f"skill{i+1}"]
            #         mastery = request.POST[f"mastery{i+1}"]
            #         if skill and mastery:
            #             Skill.objects.create(skill=skill, mastery=mastery, website=website)
            # project = request.POST["project1T"]
            # about_project = request.POST["Project1"]
            # if project and about_project:
            #     Project.objects.create(title=project, about=about_project, website=website)

            # work = request.POST["work1T"]
            # years = request.POST["work1Y"]
            # about_work = request.POST["work1"]
            # if work and years and about_work:
            #     Experience.objects.create(job=work, years=years, about=about_work, website=website)

            return redirect(f"/{website.unique_name}")

    else:
        form = CreateWebsite()

    context = {
        "form": form
    }

    return render(request, "create.html", context)

@xframe_options_exempt
def display(request, slug):
    website = Website.objects.get(unique_name=slug)
    
    if website.activation_margin and website.activation_margin < timezone.now().date():
        website.is_active = False
        website.save()

    if website.activation_deadline and (website.activation_deadline < timezone.now().date() <  website.activation_margin) and website.user==request.user.profile:
        warning = True
    else:
        warning = False

    skills = Skill.objects.filter(website=website)
    projects = Project.objects.filter(website=website)
    work = Experience.objects.filter(website=website)

    context = {
        "website": website,
        "skills": skills,
        "projects": projects,
        "works": work,
        "warning": warning
    }
    print(warning)
    try:
        if website.is_active or website.user == request.user.profile:
            return render(request, "portfolio.html", context)
        else:
            return redirect('/error')
    except:
        return redirect('/error')

@login_required
def add_skill(request, slug):
    website = Website.objects.get(unique_name=slug)
    
    
    if request.user.profile != website.user:
        return redirect("/error")
        
    else:
        skills = Skill.objects.filter(website=website)
        if request.method == "POST":
            form = AddSkill(request.POST)
            if form.is_valid():
                myform = form.save(commit=False)
                myform.website = website
                myform.save()
                return redirect(f"/{website.unique_name}")
        else:
            form = AddSkill()
        context = {
            "website": website,
            "form": form,
            "skills": skills
        }
        return render(request, "add_skill.html", context)


@login_required
def delete_skill(request, id):
    skill = Skill.objects.get(id=id)
    if request.user.profile == skill.website.user:
        website_slug = skill.website.unique_name
        skill.delete()
        return redirect(f"/{website_slug}")
    else:
        return redirect("/error")


@login_required
def delete_certificate(request, id):
    cert = Certificate.objects.get(id=id)
    if request.user.profile == cert.website.user:
        website_slug = cert.website.unique_name
        cert.delete()
        return redirect(f"/{website_slug}")
    else:
        return redirect("/error")


@login_required
def add_project(request, slug):
    website = Website.objects.get(unique_name=slug)
    if request.user.profile != website.user:
        return redirect("/error")
    else:
        projects = Project.objects.filter(website=website)
        if request.method == "POST":
            form = AddProject(request.POST, request.FILES)
            if form.is_valid():
                myform = form.save(commit=False)
                myform.website = website
                myform.save()
                return redirect(f"/{website.unique_name}")
        else:
            form = AddProject()
        context = {
            "website": website,
            "form": form,
            "projects": projects
        }
        return render(request, "projects.html", context)

@login_required
def edit_project(request, id):
    website = request.user.profile.website
    project = Project.objects.get(id=id)
    if not project.website == website:
        return redirect("/error")
    else:
        projects = Project.objects.filter(website=website)
        if request.method == "POST":
            form = AddProject(request.POST, request.FILES, instance=project)
            if form.is_valid():
                myform = form.save(commit=False)
                myform.website = website
                myform.save()
                return redirect(f"/{website.unique_name}")
        else:
            form = AddProject(instance=project)
        context = {
            "website": website,
            "form": form,
            "projects": projects
        }
        return render(request, "projects.html", context)
    
@login_required
def delete_project(request, id):
    project = Project.objects.get(id=id)
    if request.user.profile == project.website.user:
        website_slug = project.website.unique_name
        project.delete()
        return redirect(f"/{website_slug}")
    else:
        return redirect("/error")


@login_required
def add_work(request, slug):
    website = Website.objects.get(unique_name=slug)
    if request.user.profile != website.user:
        return redirect("/error")
    else:
        work = Experience.objects.filter(website=website)
        if request.method == "POST":
            form = AddExperience(request.POST, request.FILES)
            if form.is_valid():
                myform = form.save(commit=False)
                myform.website = website
                myform.save()
                return redirect(f"/{website.unique_name}")
        else:
            form = AddExperience()
        context = {
            "website": website,
            "form": form,
            "work": work
        }
        return render(request, "work_experience.html", context)


@login_required
def delete_work(request, id):
    work = Experience.objects.get(id=id)
    if request.user.profile == work.website.user:
        website_slug = work.website.unique_name
        work.delete()
        return redirect(f"/{website_slug}")
    else:
        return redirect("/error")


@login_required
def edit_info(request, slug):
    website = Website.objects.get(unique_name=slug)
    if request.user.profile == website.user:
        if request.method == "POST":
            form = EditWebsite(request.POST, request.FILES, instance=website)
            if form.errors:
                print(form.errors)
            if form.is_valid():
                myform = form.save(commit=False)
                myform.id = website.id
                myform.user = request.user.profile
                myform.save()
                return redirect(f"/{website.unique_name}")
        else:
            form = CreateWebsite(instance=website)
        context = {
            "website": website,
            "form": form
        }
        return render(request, "edit.html", context)
    else:
        return redirect("/error")


def delete_website(request, slug):
    website = Website.objects.get(unique_name=slug)
    if request.user.profile == website.user:
        website.delete()
        return redirect("/")
    else:
        return redirect("/error")


@login_required
def publish_website(request, key):
    try: 
        code = Key.objects.get(code=key) 
    except: 
        return redirect('/error')

    website = request.user.profile.website
    
    if code.plan == "Yearly" and not code.expired:
        website.is_active = True
        website.activation_deadline = timezone.now() + timedelta(days=365)
        website.activation_margin = timezone.now() + timedelta(days=365+7)
        website.save()
        code.user.coins += 5
        code.user.save()
        code.expired = True
        code.save()
        Report.objects.create(amount=500, portfolio=website, action="payment", coupon=website.user.invited)
        messages.success(request, 'Portfolio activated successfully!')
        return redirect(f"/{website.unique_name}")
    elif code.plan == "Monthly" and not code.expired:
        website.is_active = True
        website.activation_deadline = timezone.now() + timedelta(days=30)
        website.activation_margin = timezone.now() + timedelta(days=30+7)
        website.save()
        code.user.coins += 5
        code.user.save()
        code.expired = True
        code.save()
        Report.objects.create(amount=50, portfolio=website, action="payment", coupon=website.user.invited)
        messages.success(request, 'Portfolio activated successfully!')
        return redirect(f"/{website.unique_name}")
    
    elif code.plan == "Quarterly" and not code.expired:
        website.is_active = True
        website.activation_deadline = timezone.now() + timedelta(days=90) #3 months
        website.activation_margin = timezone.now() + timedelta(days=90+7) #3 months + 15 days
        website.save()
        code.user.coins += 5
        code.user.save()
        code.expired = True
        code.save()
        Report.objects.create(amount=150, portfolio=website, action="payment", coupon=website.user.invited)
        messages.success(request, 'Portfolio activated successfully!')
        return redirect(f"/{website.unique_name}")
    else:
        return redirect("/error")
    
@login_required
def publish(request):
    return render(request, "activation_options.html")

@login_required
def publish_code(request):
    return render(request, "activate.html")

@login_required
def subscribe(request, plan):
    MID = "MID-41408-888"
    if plan =="monthly": amount = 50
    if plan == "yearly": amount = 500
    if plan == "quarterly": amount = 150
    currency = "EGP"
    orderid = f"{plan}-{uuid.uuid4().hex[:8]}" 
    CustomerReference = 1
    path = '/?payment={}.{}.{}.{}'.format( MID, orderid, amount, currency )
    path = bytes(path, 'utf-8')
    secret= bytes(KASHIER_SECRET, 'utf-8')
    hash_string = hmac.new(secret, path, hashlib.sha256).hexdigest()
    redirect_url = urllib.parse.quote(f"https://sirati.opindustries.space/{request.user.profile.website.unique_name}")

    context = {
        "mid": MID,
        "hash_string": hash_string,
        "amount": amount,
        "currency": currency,
        "orderid": orderid,
        "plan": plan,
        "encoded_url": redirect_url
    }

    return render(request, "payment.html", context)

# Copy and paste this code in your backend
import hmac
import hashlib


@csrf_exempt
@require_POST
def kashier_webhook(request, plan):
    # Parse JSON or form data
    try:
        data = json.loads(request.body.decode("utf-8"))["data"]
    except json.JSONDecodeError:
        data = request.POST.dict()

    print(data)

    if not data:
        return HttpResponseBadRequest("Empty payload")

    # # Verify signature
    # if not validate_signature(data, KASHIER_SECRET):
    #     return JsonResponse({"error": "Invalid signature"}, status=403)
    status = data.get("status")
    print(status)

    if status != "SUCCESS":
        return JsonResponse({"message": "Payment failed"}, status=200)

    # Lookup website by order_id or user_id (adjust as needed)
    try:
        website = request.user.profile.website  # example
    except Website.DoesNotExist:
        return JsonResponse({"error": "Website not found"}, status=400)

    # Plan-based activation
    plan_days = {"monthly": 30, "quarterly": 90, "yearly": 365}
    plan_amounts = {"monthly": 50, "quarterly": 150, "yearly": 500}

    plan_lower = plan.lower()
    if plan_lower not in plan_days:
        return JsonResponse({"error": "Unknown plan"}, status=400)

    website.is_active = True
    website.activation_deadline = timezone.now() + timedelta(days=plan_days[plan_lower])
    website.activation_margin = timezone.now() + timedelta(days=plan_days[plan_lower]+7)
    website.save()

    Report.objects.create(
        amount=plan_amounts[plan_lower],
        portfolio=website,
        action="payment",
        coupon=website.user.invited
    )

    print(f"✅ Website {website.id} activated for plan {plan_lower}")
    return JsonResponse({"message": f"Website activated for plan {plan_lower}"}, status=200)

@login_required
def admin_dashboard(request):
    user = request.user.profile
    if not request.user.is_superuser:
        return redirect("/error")
    else:
        yearly_codes = Key.objects.filter(plan="Yearly", user=user)
        monthly_codes = Key.objects.filter(plan="Monthly", user=user)
        quarterly_codes = Key.objects.filter(plan="Quarterly", user=user)

        if request.method == "POST":
            form = Create_Key(request.POST, request.FILES)
            print("received post")
            print(form.errors)
            if form.is_valid():
                print("form is valid")
                myform = form.save(commit=False)
                myform.user = request.user.profile
                myform.save()
        else:
            form = Create_Key()
        
        context = {
            "yearly_codes": yearly_codes,
            "monthly_codes": monthly_codes,
            "quarterly_codes": quarterly_codes,
            "form": form,
        }

        return render(request, "dashboard.html", context)

@login_required
def clear_expired(request):
    user = request.user
    if not user.is_superuser:
        return redirect('/error')
    else:
        keys = Key.objects.filter(user=user.profile, expired=True)
        keys.delete()
        return redirect('/admin_dashboard')

@csrf_exempt
@require_POST
def contact_website(request, slug):
    """
    Accepts JSON: { "name": "...", "email": "...", "message": "..." }
    Sends an email to the portfolio owner (website.user.email or website.email).
    """
    website = get_object_or_404(Website, unique_name=slug)

    # parse JSON body
    try:
        payload = json.loads(request.body.decode() or "{}")
    except Exception:
        return HttpResponseBadRequest("Invalid JSON payload.")

    name = (payload.get("name") or "").strip()
    sender_email = (payload.get("email") or "").strip()
    message_text = (payload.get("message") or "").strip()

    if not (name and sender_email and message_text):
        return JsonResponse({"status": "error", "message": "Please provide name, email and message."}, status=400)

    try:
        validate_email(sender_email)
    except ValidationError:
        return JsonResponse({"status": "error", "message": "Invalid email address."}, status=400)

    # pick recipient: prefer related user email, fallback to website.email (if you have it)
    recipient = None
    try:
        recipient = getattr(website.user, "email", None)
    except Exception:
        recipient = None

    if not recipient:
        recipient = getattr(website, "email", None)

    if not recipient:
        logger.error("No recipient email configured for website %s", unique_name)
        return JsonResponse({"status": "error", "message": "Owner email not configured."}, status=500)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@yourdomain.com")

    subject = f"[Sirati] Message for {website.full_name or website.unique_name} — from {name}"
    body = (
        f"You have a new message from your Sirati portfolio page.\n\n"
        f"Website: {website.full_name or website.unique_name} ({getattr(website, 'unique_name')})\n"
        f"From: {name}\n"
        f"Email: {sender_email}\n\n"
        f"Message:\n{message_text}\n\n"
        f"---\nThis message was delivered via Sirati."
    )

    email_msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[recipient],
        headers={"Reply-To": sender_email},
    )

    try:
        email_msg.send(fail_silently=False)
        return JsonResponse({"status": "ok", "message": "Message delivered — the owner will receive an email."})
    except Exception:
        logger.exception("Failed to send contact email for website %s", unique_name)
        return JsonResponse({"status": "error", "message": "Failed to send message. Please try again later."}, status=500)