from django.contrib import admin
from .models import ClientName, Owner, NewAbonent, Platform, ViPNetNetNumber
# from Request.admin import NewReqInline

# class OwnerAdmin(admin.ModelAdmin):
#     inlines = [
#         NewReqInline,
#     ]

admin.site.register(ClientName)
admin.site.register(Owner)
admin.site.register(NewAbonent)
admin.site.register(Platform)
admin.site.register(ViPNetNetNumber)
