from app.admin import admin
from app.admin import ModelAdmin
from tasks.models import Task
from tasks.models import TaskUser


@admin.register(Task, TaskUser)
class TaskAdmin(ModelAdmin):
    pass
