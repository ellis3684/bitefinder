from django.contrib import admin

from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'name', 'calories')
    search_fields = ('restaurant__name', 'name')
