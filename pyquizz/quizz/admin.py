from django.contrib import admin

from .models import Group, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def groups_display(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])
    groups_display.short_description = "Groupes"

    list_display = ('email', 'groups_display')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('persons',)
