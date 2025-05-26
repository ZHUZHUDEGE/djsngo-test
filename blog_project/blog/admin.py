from django.contrib import admin
from .models import Article
from django.utils.html import format_html


class ArticleAdmin(admin.ModelAdmin):
    # 列表页显示字段
    list_display = ('title', 'author', 'created_at', 'updated_at', 'published', 'display_tags')
    # 可点击链接字段
    list_display_links = ('title',)
    # 可过滤字段
    list_filter = ('published', 'created_at', 'author')
    # 可搜索字段
    search_fields = ('title', 'content', 'author__username')

    # 分页设置
    list_per_page = 25

    # 表单字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'author', 'published')
        }),
        ('内容', {
            'fields': ('content', 'tags')
        }),
        ('元数据', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # 自动填充字段
    prepopulated_fields = {}

    # 自定义方法显示tags
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = '标签'

    # 自动设置当前用户为作者
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # 如果是新建而不是修改
            obj.author = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)