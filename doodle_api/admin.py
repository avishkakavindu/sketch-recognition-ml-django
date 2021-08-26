from django.contrib import admin
from doodle_api.models import Label


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    pass