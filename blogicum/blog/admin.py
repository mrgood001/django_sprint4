from django.contrib import admin
from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published')


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Location)
