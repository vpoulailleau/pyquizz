from django.contrib import admin

from .models import Group, Person

admin.site.register(Person)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
