from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.utils.encoding import uri_to_iri
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from .models import Poll, PollQuestionAnswer, PollQuestionChoices
from .permissions import TeacherPermission

from .serializers import (
    PollSerializer,
    AnswerPostSerializer,
    PollHistorySerializer,
    PollQuestionAnswerHistorySerializer,
)


class PollsView(LoginRequiredMixin, ListAPIView):
    login_url = "http://127.0.0.1:8000/users/sign_in/"
    serializer_class = PollSerializer
    queryset = Poll.objects


class PollDetailView(LoginRequiredMixin, RetrieveAPIView):
    login_url = "http://127.0.0.1:8000/userusers/sign_in/"
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

    @atomic
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
            return Response(
                data="ok", status=status.HTTP_201_CREATED, headers={"status": "created"}
            )
        else:
            return Response(serializer_ans.errors, status=status.HTTP_400_BAD_REQUEST)


class PollHistoryView(LoginRequiredMixin, ListAPIView):
    login_url = "http://127.0.0.1:8000/users/sign_in/"
    serializer_class_orig = PollHistorySerializer
    serializer_class_teacher = PollQuestionAnswerHistorySerializer
    permission_classes = [TeacherPermission]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id", self.request.user)
        poll_title_raw = self.kwargs.get("poll_title", None)
        if user_id and poll_title_raw:
            poll_title = uri_to_iri(poll_title_raw)
            qs = Poll.objects.filter(
                Q(questions__answer__user=user_id) & Q(poll_title=poll_title)
            ).distinct()
        else:
            qs = Poll.objects.filter(
                questions__answer__user=user_id,
            ).distinct()

        return qs

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.serializer_class_orig
        else:
            return self.serializer_class_teacher

    def get_serializer_context(self):
        if self.kwargs:
            return {
                "request": self.request,
                "format": self.format_kwarg,
                "view": self,
                "custom_context": self.kwargs,
            }
        return super().get_serializer_context()

    def get(self, request, *args, **kwargs):
        """Check if no kwargs, should check if exists,
         otherwise data in kwargs is already trustworthy """
        if not any(list(kwargs.values())):
            has_answered = Poll.objects.filter(
                questions__answer__user=request.user
            ).exists()
            if not has_answered:
                return redirect("PollsView")
        return super().get(request, *args, **kwargs)

    @atomic
    def delete(self, request, *arg, **kwargs):
        """drop down current user results"""
        PollQuestionAnswer.objects.filter(
            Q(user=self.kwargs["user_id"])
            & Q(question__poll__poll_title=uri_to_iri(self.kwargs["poll_title"]))
        ).delete()

        return Response(data={"status": "OK"}, status=status.HTTP_202_ACCEPTED)
