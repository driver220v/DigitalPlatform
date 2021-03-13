from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from .models import Poll, PollQuestionAnswer, PollQuestionChoices

from .serializers import PollSerializer, AnswerPostSerializer, PollHistorySerializer


class PollsView(LoginRequiredMixin, ListAPIView):
    login_url = "http://127.0.0.1:8000/users/sign_in/"
    serializer_class = PollSerializer
    queryset = Poll.objects


# def get_absolute_url(app: str, view: str):
#     from django.urls import reverse
#     return reverse(f'{app}.views.{view}')


class PollDetailView(LoginRequiredMixin, RetrieveAPIView):
    login_url = "http://127.0.0.1:8000/users/sign_in/"
    queryset = Poll.objects
    serializer_class_polls = PollSerializer
    serializer_class_answers = AnswerPostSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.serializer_class_polls
        else:
            return self.serializer_class_answers

    def get(self, request, *args, **kwargs):
        has_answered = Poll.objects.filter(
            questions__answer__user=request.user
        ).exists()
        if has_answered:
            return redirect("HomeView")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        serializer_ans = self.serializer_class_answers(
            instance=PollQuestionChoices.objects.select_related("question__poll")
            .filter(question__poll_id=self.kwargs["pk"])
            .values_list("question__poll_id", "question_id", "id")
            .distinct(),
            data=request.data,
        )
        if serializer_ans.is_valid():
            with transaction.atomic():
                PollQuestionAnswer.objects.bulk_create(
                    [
                        PollQuestionAnswer(
                            user=request.user,
                            question_id=int(id_question),
                            choice_id=id_choice,
                        )
                        for id_question, id_choice in serializer_ans.validated_data[
                            "answers"
                        ].items()
                    ]
                )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_ans.errors, status=status.HTTP_400_BAD_REQUEST)


class PollHistoryView(LoginRequiredMixin, ListAPIView):
    login_url = "http://127.0.0.1:8000/users/sign_in/"
    serializer_class = PollHistorySerializer

    # queryset = Poll.objects

    def get_queryset(self):
        qs = Poll.objects.prefetch_related(
            Prefetch(
                "questions__answer",
                queryset=PollQuestionAnswer.objects.filter(user_id=self.request.user),
            )
        )
        return qs

    def get(self, request, *args, **kwargs):
        has_answered = Poll.objects.filter(
            questions__answer__user=request.user
        ).exists()
        if has_answered:
            return super().get(request, *args, **kwargs)
        return redirect("PollsView")

    # Poll.objects.prefetch_related(Prefetch('questions',
    #                                        queryset=PollQuestion.objects.prefetch_related("choices").
    #                                        filter(Q(choices__question__id__in=[self.kwargs['pk']]) & Q(
    #                                            poll_id=self.kwargs['pk'])),
    #                                        to_attr='p_questions')).get(pk=self.kwargs['pk']),

    # Poll.objects.prefetch_related(Prefetch('questions',
    #                                        queryset=PollQuestion.objects.filter(
    #                                            poll_id=self.kwargs['pk']),
    #                                        to_attr='p_questions')).get(pk=self.kwargs['pk']),
