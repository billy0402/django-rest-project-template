from django.contrib import admin

from server.app.todo import models as todo_models


@admin.register(todo_models.Task)
class TaskAdmin(admin.ModelAdmin[todo_models.Task]):
    list_display = ("title", "is_finish")
    list_filter = ("is_finish", "tags", "category")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)


@admin.register(todo_models.Tag)
class TagAdmin(admin.ModelAdmin[todo_models.Tag]):
    pass


@admin.register(todo_models.Category)
class CategoryAdmin(admin.ModelAdmin[todo_models.Category]):
    pass
