from django.contrib import admin
from.models import Website, Skill, Experience, Project, Certificate, PublishRequest, Key, Report, Lead
# Register your models here.

admin.site.register(Website)
admin.site.register(Key)
admin.site.register(PublishRequest)
admin.site.register(Skill)
admin.site.register(Certificate)
admin.site.register(Project)
admin.site.register(Experience)
admin.site.register(Report)
admin.site.register(Lead)