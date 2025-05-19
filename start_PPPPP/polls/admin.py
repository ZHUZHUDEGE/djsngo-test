from django.contrib import admin
from .models import Question, Choice, Vote
# Register your models here.


class ChoiceInline(admin.TabularInline):  # 也可以用 admin.StackedInline
    model = Choice
    extra = 3  # 默认显示3个空白选项字段


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'author', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
        ('Author', {'fields': ['author']}),
         ]
    readonly_fields = ('pub_date',)
    inlines = [ChoiceInline]  # 在问题编辑页内联编辑选项

    # 自动设置当前用户为作者

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'choice', 'voted_date')
    list_filter = ['voted_date']
    search_fields = ['user__username', 'choice__choice_text']


admin.site.register(Question,QuestionAdmin)
admin.site.register(Vote,VoteAdmin)