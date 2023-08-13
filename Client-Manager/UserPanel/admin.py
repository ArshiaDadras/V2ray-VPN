from django.contrib import admin
from .models import Customer
from django.db import models
from django import forms

class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Information', {'fields': ['name', 'mobile', 'email']}),
        ('Payment Details', {'fields': ['destination_card', 'payment_code', 'plan']}),
        ('Payment Verification', {'fields': ['verified']}),
    ]
    formfield_overrides = {
        models.BooleanField: {'widget': forms.Select(choices=[(True, 'Yes'), (False, 'No')])},
    }
    list_display = ('full_name', 'plan', 'referral', 'verified')
    list_filter = ('plan', 'destination_card', 'verified')
    search_fields = ('name', 'mobile')
    ordering = ('name',)

    def full_name(self, obj):
        return ' '.join(obj.name.split(' - '))
    
    def referral(self, obj):
        Artin = [
            '6221061059749541',
        ]
        return 'Artin' if obj.destination_card in Artin else 'Arshia'

admin.site.register(Customer, CustomerAdmin)