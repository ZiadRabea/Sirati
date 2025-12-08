from django.db import models
from Accounts.models import Profile
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.


class Website(models.Model):
    unique_name = models.SlugField(max_length=500, unique=True)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True)
    is_active = models.BooleanField(default=False)
    cv_url = models.URLField(null=True, blank=True)
    full_name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to="profile_pictures", storage=MediaCloudinaryStorage)
    current_job = models.CharField(max_length=500)
    about = models.TextField(max_length=2000)
    email = models.EmailField()
    age = models.IntegerField()
    analytics = models.CharField(max_length=200, null=True, blank=True)
    adsense = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fb = models.URLField(null=True, blank=True)
    insta = models.URLField(blank=True, null=True)
    tele = models.URLField(blank=True, null=True)
    wp = models.URLField(null=True, blank=True)


class Skill(models.Model):
    skill = models.CharField(max_length=100)
    mastery = models.IntegerField()
    website = models.ForeignKey(Website, on_delete=models.CASCADE)


class Project(models.Model):
    title = models.CharField(max_length=100)
    about = models.TextField(max_length=2000)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)


class Certificate(models.Model):
    cert = models.ImageField(upload_to="Certificates", storage=MediaCloudinaryStorage)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)


class Experience(models.Model):
    job = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)


class PublishRequest(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='publish_requests')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    plan = models.CharField(max_length=64, default='trial_7')
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"PublishRequest({self.website}, {self.user}, {self.created_at})"
    
