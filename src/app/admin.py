from django.contrib import admin
from .models import Post, Category
# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'slug', 'category', 'created')
    list_filter = ('author', 'content', 'category')
    search_fields = ('author', 'content', 'category')
    prepopulated_fields = {'slug': ('author','id','content')}
    raw_id_fields = ('category',)
    filter_horizontal = ()
    fieldsets = ()

    class Meta:
        model = Post


admin.site.register(Post, PostAdmin)
admin.site.register(Category)

