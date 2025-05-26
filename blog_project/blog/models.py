import markdown
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from taggit.managers import TaggableManager


# Create your models here.
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    # tags = models.CharField(max_length=100, blank=True)
    tags = TaggableManager()  # 替换原来的tags字段
    views = models.PositiveIntegerField(default=0)  # 新增，用于统计浏览量
    # 原有字段保持不变...
    content_markdown = models.TextField(blank=True, editable=False)  # 新增字段，用于存储转换后的HTML

    def save(self, *args, **kwargs):
        # 保存时自动将Markdown转换为HTML
        super().save(*args, **kwargs)
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
        self.content_markdown = markdown.markdown(
            self.content,
            extensions=extensions,
            output_format='html'
        )
        super().save(*args, **kwargs)

    def get_content_as_markdown(self):
        return mark_safe(self.content_markdown)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])