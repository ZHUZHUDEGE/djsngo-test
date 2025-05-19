# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import F
from .models import Question, Choice, Vote
from .forms import QuestionForm, ChoiceForm


@login_required
def index(request):
    questions = Question.objects.all().order_by('-pub_date')
    return render(request, 'polls/index.html', {'questions': questions})


@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.creator = request.user
            question.save()
            print(f">>>>>>新问题ID: {question.id}")  # 调试用，查看是否生成了ID
            return redirect('polls:add_choices', question_id=question.id)
    else:
        form = QuestionForm()
    return render(request, 'polls/create_question.html', {'form': form})


@login_required
def add_choices(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST,question=question)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            if 'add_another' in request.POST:
                return HttpResponseRedirect(reverse('polls:add_choices', args=[question.id]))
            else:
                return redirect('polls:index')

            # 移除原来的重定向逻辑，由表单的formaction处理
            #　return HttpResponseRedirect(request.path_info)  # 刷新当前页面
    else:
        form = ChoiceForm(request.POST or None, question=question)
    return render(request, 'polls/add_choices.html', {
        'question': question,
        'form': form,
        'choices': question.choice_set.all()
    })


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # 检查用户是否是提问者
    if question.creator == request.user:
        return JsonResponse({'error': 'creator_vote', 'message': "您不能投票自己创建的问题。"}, status=403)

    # 获取用户选择的选项
    selected_choices = request.POST.getlist('choice')  # 支持多选
    if not selected_choices:
        return JsonResponse({'error': 'no_choice', 'message': "您必须选择至少一个选项。"}, status=400)

    # 检查选择数量是否符合规则
    if len(selected_choices) < question.min_choices or len(selected_choices) > question.max_choices:
        return JsonResponse({
            'error': 'invalid_choice_count',
            'message': f"您必须选择至少 {question.min_choices} 个选项，最多 {question.max_choices} 个选项。"
        }, status=400)

    # 检查用户是否已经投票超过限制
    user_votes_count = Vote.objects.filter(user=request.user, question=question).count()
    if user_votes_count + len(selected_choices) > question.max_votes_per_user:
        return JsonResponse({
            'error': 'vote_limit_exceeded',
            'message': f"您最多只能投 {question.max_votes_per_user} 票。"
        }, status=400)

    # 查询所有选择的选项
    choices = Choice.objects.filter(pk__in=selected_choices, question=question)

    # 检查每个选项是否超过最大票数限制
    for choice in choices:
        user_choice_votes = Vote.objects.filter(user=request.user, choice=choice).count()
        if user_choice_votes >= choice.max_votes_per_choice:
            return JsonResponse({
                'error': 'choice_vote_limit_exceeded',
                'message': f"选项 '{choice.choice_text}' 已达到最大投票限制。"
            }, status=400)

    # 创建投票记录并更新票数
    votes_to_create = []
    for choice in choices:
        votes_to_create.append(Vote(user=request.user, question=question, choice=choice))
        choice.votes = F('votes') + 1  # 使用 F 表达式避免竞争条件

    # 批量创建投票记录
    Vote.objects.bulk_create(votes_to_create)

    # 批量更新票数
    Choice.objects.bulk_update(choices, ['votes'])

    # 投票成功后重定向到结果页面
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})