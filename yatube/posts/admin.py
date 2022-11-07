from django.contrib import admin

from .models import Group, Post, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('pub_date', 'author_id')
    empty_value_display = '-пусто-'
    list_editable = ('group',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_editable = (
        'title',
        'slug',
        'description',
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display: (
        'pk',
        'text',
        'author',
        'created'
    )
    
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display: (
        'pk',
        'author',
        'user',
    )