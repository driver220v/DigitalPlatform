from django import forms

from polls.models import Poll, PollQuestion, PollQuestionChoices


class PollForm(forms.ModelForm):
    # signUp = forms.BooleanField(required=True)
    #
    # def __init__(self, *args, **kwargs):
    #     super(PollForm, self).__init__(*args, **kwargs)
    #     self.fields['name'].queryset = Poll.objects.all()

    class Meta:
        model = Poll
        fields = '__all__'
        exclude = ('choice_status', 'enrolled_users')


#
class PollQuestionForm(forms.ModelForm):
    class Meta:
        model = PollQuestion
        fields = "__all__"


class PollQuestionChoicesForm(forms.ModelForm):
    class Meta:
        model = PollQuestionChoices
        fields = "__all__"

# questions = forms.ModelMultipleChoiceField(queryset=PollQuestion.objects.all())
# poll = forms.

# def __init__(self, *args, **kwargs):
#     super(PollQuestionChoiceForm, self).__init__(*args, **kwargs)
#     print(self.fields['question'].choices, dir(self.fields['question']))
#     for i in self.fields['question'].choices:
#         print(i)
#     self.fields['question'].queryset = PollQuestion.objects.none()


#    poll_n = None
#    question_n = None
#    # choices = forms.MultiValueField(PollQuestionChoices)
#
#    def __init__(self, *args, **kwargs):
#        super(PollQuestionChoicesForm, self).__init__(*args, **kwargs)
#        for poll in list(self.data):
#            self.poll_n = poll.question.poll
#            print(self.poll_n)
#            # self.questions_n = questions.question
#        print(self.poll_n)
