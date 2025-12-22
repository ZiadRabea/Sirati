"""infinitfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portfolio.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('error/', error),
    path('admin_dashboard/', admin_dashboard),
    path('admin_dashboard/clear', clear_expired),
    path('publish/', publish),
    path('payment/<str:plan>/<str:slug>', subscribe),
    path('kashier/webhook/<str:plan>', kashier_webhook),
    path('activate/code', publish_code),
    path('publish/<str:key>', publish_website, name='website_publish'),
    path('<str:slug>/contact/', contact_website, name='website_contact'),
    path('create/', create),
    path('<str:slug>/skills/', add_skill),
    path('<str:slug>/projects', add_project),
    path('certificate/<int:id>/delete', delete_certificate),
    path('skills/<int:id>/delete', delete_skill),
    path('projects/<int:id>/delete', delete_project),
    path('projects/<int:id>/edit', edit_project),
    path('<str:slug>/work', add_work),
    path('work/<int:id>/delete', delete_work),
    path('<str:slug>/edit', edit_info),
    path('<str:slug>/delete', delete_website),
    path('<str:slug>/', display),
    path('accounts/', include("Accounts.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
