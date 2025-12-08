from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .forms import *
from .filters import *
from .models import *
from django.conf import settings
from django.core.mail import send_mail, mail_admins, BadHeaderError
import logging

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


def display(request, slug):
    website = Website.objects.get(unique_name=slug)
    skills = Skill.objects.filter(website=website)
    projects = Project.objects.filter(website=website)
    work = Experience.objects.filter(website=website)
    certs = Certificate.objects.filter(website=website)
    context = {
        "website": website,
        "skills": skills,
        "projects": projects,
        "works": work,
        "certs": certs
    }
    try:
        if website.is_active or website.user == request.user.profile:
            return render(request, "portfolio.html", context)
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
@require_POST
def publish_website(request, slug):
    website = get_object_or_404(Website, unique_name=slug)

    # ensure user owns the site
    if request.user.profile != website.user:
        return HttpResponseForbidden('Not allowed')

    # compose email
    subject = f"Publish request for site: {website.full_name or website.unique_name}"
    body_lines = [
        f"User: {request.user.get_full_name() or request.user.username} <{request.user.email}>",
        f"Website: {website.unique_name}",
        f"Display name: {website.full_name or '—'}",
        f"Requested plan: trial_7",
        "",
        "To approve this request, visit the admin dashboard or use your internal workflow.",
    ]
    message = "\n".join(body_lines)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@yourdomain.com"

    try:
        # send a confirmation/receipt to the requester (so "you" get the email)
        if request.user.email:
            send_mail(
                subject=subject,
                message=(
                    f"Thanks — we've received your publish request.\n\n"
                    f"{message}\n\n"
                    "We'll review and get back to you shortly."
                ),
                from_email=from_email,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

        # also notify site admins (optional — uses ADMINS from settings)
        try:
            send_mail(
                subject="New Publish Request",
                message=(
                    f"Publish Request {website.unique_name} by {request.user.email}"
                ),
                from_email=from_email,
                recipient_list=["ziadrabeay1@gmail.com"],
                fail_silently=True,
            )
        except Exception:
            # mail_admins may raise if ADMINS not configured; swallow but log
            logger.exception("mail_admins failed for publish request")

        return JsonResponse({
            "status": "ok",
            "message": "Publish request sent. A confirmation email has been delivered."
        })
    except BadHeaderError:
        logger.exception("BadHeaderError sending publish email")
        return JsonResponse({"status": "error", "message": "Invalid header in email."}, status=500)
    except Exception:
        logger.exception("Failed to send publish request email")
        return JsonResponse({"status": "error", "message": "Failed to send email. Please try again later."}, status=500)