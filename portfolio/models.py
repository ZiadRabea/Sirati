from django.db import models
from Accounts.models import Profile
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.contrib.postgres.fields import ArrayField
from django.utils.crypto import get_random_string
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
# Create your models here.


class Website(models.Model):
    unique_name = models.SlugField(max_length=500, unique=True)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True)
    is_active = models.BooleanField(default=False)
    activation_deadline = models.DateField(null=True, blank=True)
    activation_margin = models.DateField(null=True, blank=True)
    birthday = models.DateField()
    cv_url = models.URLField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pictures", storage=MediaCloudinaryStorage)
    current_job = models.CharField(max_length=500)
    about = models.TextField(max_length=2000)
    email = models.EmailField()
    fb = models.URLField(null=True, blank=True)
    insta = models.URLField(blank=True, null=True)
    tele = models.URLField(blank=True, null=True)
    wp = models.URLField(null=True, blank=True)

    @property
    def age(self):
        """Return age in years (int) or None if birthday not set."""
        if not self.birthday:
            return None
        today = date.today()
        # compute difference in years, subtract 1 if birthday hasn't occurred yet this year
        years = today.year - self.birthday.year
        has_had_birthday = (today.month, today.day) >= (self.birthday.month, self.birthday.day)
        return years if has_had_birthday else years - 1
    
class Skill(models.Model):
    skill = models.CharField(max_length=100)
    mastery = models.IntegerField(validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ])
    website = models.ForeignKey(Website, on_delete=models.CASCADE)


class Project(models.Model):
    title = models.CharField(max_length=100)
    about = models.TextField(max_length=2000)
    tech = ArrayField(models.CharField(max_length=100), null=True, blank=True, default=list)
    image =  models.ImageField(upload_to="profile_pictures", storage=MediaCloudinaryStorage, null=True, blank=True)
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
    
class Key(models.Model):
    CODE_LENGTH = 10
    
    def generate_random_code():
        return get_random_string(Key.CODE_LENGTH)
    
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)

    code = models.CharField(
        max_length=CODE_LENGTH,
        unique=True,  # Consider making it unique if it's an identifier
        default=generate_random_code,  # Pass the function itself, not generate_random_code()
        editable=False, # Optional: if you don't want it to be editable in forms/admin
        null=True,
        blank=True
    )
    expired = models.BooleanField(default=False, null=True, blank=True)
    plans = (("Monthly","Monthly"),("Yearly","Yearly"),("Quarterly","Quarterly"))
    plan = models.CharField(choices=plans, max_length=10)


class Report(models.Model):
    coupon = models.CharField(max_length=100, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    portfolio = models.ForeignKey(Website, on_delete=models.CASCADE)
    actions = (("payment", "payment"),("withdrawal", "withdrawal"))
    action = models.CharField(max_length=100, choices=actions)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EGP {self.amount} | {self.action} | {self.portfolio.user}"

class Lead(models.Model):
    email = models.EmailField()
    payment_success = models.BooleanField()