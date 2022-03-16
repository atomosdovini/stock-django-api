from django.contrib import admin
from .models import Research, Sector, Stock, Recommendation
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


# # Register your models here.
# @admin.register(Research)
# class ResearchAdmin(admin.ModelAdmin):
#     list_per_page = 15 

# @admin.register(Sector)
# class SectorAdmin(admin.ModelAdmin):
#     list_per_page = 15    

# @admin.register(Stock)
# class StockAdmin(admin.ModelAdmin):
#     list_per_page = 15  

# @admin.register(Recommendation)
# class RecommendationAdmin(admin.ModelAdmin):
#     list_per_page = 15 
# Unregister the provided model admin
# admin.site.unregister(User)

