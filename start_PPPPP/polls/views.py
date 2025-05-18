# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
            question.save()
            return redirect('polls:add_choices', question_id=question.id)
    else:
        form = QuestionForm()
    return render(request, 'polls/create_question.html', {'form': form})


@login_required
def add_choices(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            if 'add_another' in request.POST:
                return redirect('add_choices', question_id=question.id)
            else:
                return redirect('index')
    else:
        form = ChoiceForm()
    return render(request, 'polls/add_choices.html', {
        'question': question,
        'form': form,
        'choices': question.choice_set.all()
    })


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # 检查是否已经投过票
        if Vote.objects.filter(user=request.user, choice__question=question).exists():
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You have already voted on this question.",
            })

        selected_choice.votes += 1
        selected_choice.save()
        Vote.objects.create(user=request.user, choice=selected_choice)
        return redirect('results', question_id=question.id)


@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})