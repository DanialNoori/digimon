from django.contrib import admin
from .models import Category, SubCategory, SubGroup, Attribute, Group, Option
# Register your models here.


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubGroup)
admin.site.register(Attribute)
admin.site.register(Group)
admin.site.register(Option)