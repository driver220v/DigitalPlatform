from django.contrib import admin

# Register your models here.
from polls.models import Poll, PollQuestion, PollQuestionChoices

admin.site.register(Poll)
admin.site.register(PollQuestion)
admin.site.register(PollQuestionChoices)