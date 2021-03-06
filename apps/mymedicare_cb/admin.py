from django.contrib import admin
from .models import AnonUserState

__author__ = "Alan Viars"


class AnonUserStateAdmin(admin.ModelAdmin):

    list_display = ('state', 'next_uri')
    search_fields = ('state', 'next_uri')


admin.site.register(AnonUserState, AnonUserStateAdmin)
