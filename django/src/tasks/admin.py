from django.contrib import admin
from app.admin import ModelAdmin, admin
from tasks.models import Task, TaskCost, TaskStatus, TaskUser


@admin.register(Task, TaskCost, TaskStatus, TaskUser)
class TaskAdmin(ModelAdmin):
    # fields = [
    #     "name",
    # ]
    pass
