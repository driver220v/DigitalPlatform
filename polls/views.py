from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
import json
from .forms import PollForm, PollQuestionChoicesForm
# Create your views here.
from django.views import View

from .models import Poll, PollQuestionChoices
from django.views.generic import ListView
from django.shortcuts import render


class PollsView(LoginRequiredMixin, ListView):
    login_url = '/sign_in/'
    queryset = PollQuestionChoices.objects.select_related('question__poll')
    # for i in queryset:
    #     print(dir(i))
    #     print(i.name)
    #     print(i.poll.name)
        # print(i.question.poll)
        # print(i.question)
        # print(i.choice_name)
    #queryset = Poll.objects.prefetch_related('poll')
    template_name = 'polls/index2.html'


    # def get(self, request):
    #     # data = PollQuestionChoices.objects.prefetch_related('question__poll')
    #     form = PollForm()
    #     return render(request, 'polls/index2.html', context={'form': form})

    def post(self, request):
        print(request.POST)
        return HttpResponse('ok')

# for poll_data in data:
#     poll_name = poll_data.question.poll
#     question_n = poll_data.question
#     choice_n = poll_data.choice_name
#     if poll_name in d:
#         if question_n in d[poll_name]:
#             if choice_n not in d[poll_name][question_n]:
#                 d[poll_name][question_n].append(choice_n)
#         else:
#             d[poll_name][question_n] = [choice_n]
#     else:
#         d[poll_name] = {question_n: [choice_n]}
