import itertools
from collections import defaultdict

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.views.generic import detail
from rest_framework import serializers

from .models import Poll, PollQuestion, PollQuestionChoices, PollQuestionAnswer


# ________________________ ListAPIView Serializers ____________________________________ #


class PollQuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionAnswer
        fields = "__all__"


class PollQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionChoices
        exclude = ("is_correct",)


class PollQuestionSerializer(serializers.ModelSerializer):
    choices = PollQuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = PollQuestion
        exclude = ("poll",)


class PollSerializer(serializers.ModelSerializer):
    questions = PollQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = "__all__"


# ________________________ APIView Serializers ____________________________________ #


class AnswerPostSerializer(serializers.Serializer):
    answers = serializers.DictField()

    def __init__(self, *args, **kwargs):
        super(AnswerPostSerializer, self).__init__(*args, **kwargs)
        self.fields["answers"].validators.append(self.validate_questions_data_exists)
        self.fields["answers"].validators.append(self.validate_correlation)

    # validate that each choice_id corresponds to question_id
    def validate_correlation(self, answer_data: dict, raise_exception=None):
        for question_id, choice_id in answer_data.items():
            if choice_id not in list(self.poll_d.values())[0][int(question_id)]:
                detail_descr = "Invalid choice ID. Choice ID is not applicable for this Question ID"
                raise serializers.ValidationError(detail_descr, code=400)

    # validate presence of choices_ids and questions_ids in a selected poll
    def validate_questions_data_exists(self, answer_data: dict, raise_exception=None):
        for poll_id, question_data in self.poll_d.items():
            if any([int(i) for i in list(answer_data.keys())]) not in list(
                question_data.keys()
            ):
                detail_descr = "Choice ID is not applicable for this Poll"
                raise serializers.ValidationError(detail_descr, code=400)

            if any(list(answer_data.values())) not in list(
                itertools.chain.from_iterable(question_data.values())
            ):
                detail_descr = "Question ID is not applicable for this Poll"
                raise serializers.ValidationError(detail_descr, code=400)

    def is_valid(self, *args, raise_exception=False, **kwargs):
        self.get_ids_map()
        return super().is_valid()

    def save(self, **kwargs):
        with transaction.atomic():
            request = kwargs["request"]

            PollQuestionAnswer.objects.bulk_create(
                [
                    PollQuestionAnswer(
                        user=request.user, question_id=id_question, choice_id=id_choice
                    )
                    for id_question, id_choice in request.POST.items()
                ]
            )

    def get_ids_map(self):
        # poll_d = represent: poll_id:{question_id: [choice_id]}
        self.poll_d = {}
        for relation_t in list(self.instance):
            poll_id, question_id, choice_id = relation_t
            if poll_id not in self.poll_d:
                self.poll_d[poll_id] = {question_id: [choice_id]}
            else:
                if question_id in self.poll_d[poll_id]:
                    self.poll_d[poll_id][question_id].append(choice_id)
                else:
                    self.poll_d[poll_id].update({question_id: [choice_id]})

    class Meta:
        model = PollQuestionAnswer


# _______________________________________________________________________________________#


class PollQuestionAnswerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionAnswer
        fields = "__all__"


class PollQuestionChoiceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionChoices
        exclude = ("is_correct",)


class PollQuestionHistorySerializer(serializers.ModelSerializer):
    choices = PollQuestionChoiceHistorySerializer(many=True, read_only=True)
    answer = PollQuestionAnswerHistorySerializer(many=True, read_only=True)

    class Meta:
        model = PollQuestion
        exclude = ("poll",)


class PollHistorySerializer(serializers.ModelSerializer):
    questions = PollQuestionHistorySerializer(many=True, read_only=True)
    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        # todo вывод процента правильных к неерпавильным
        total_q = self.instance.first().questions.count()
        choices_status = PollQuestionChoices.objects.filter(
            question__poll_id=self.instance.first().id
        ).values_list("question_id", "id", "is_correct")
        target_dict = defaultdict(list)
        for i, _ in enumerate(choices_status):
            if choices_status[i][2]:
                target_dict[choices_status[i][0]].append(choices_status[i][1])
        # correct = 2
        # if total!=0:
        #     return (correct / total)*100

    class Meta:
        model = Poll
        fields = "__all__"


# PollQuestionChoices.objects.prefetch_related('answer').filter(
#     Q(question__poll_id=obj.id) & Q(question__answer__user_id=self.instance)
#   ).values_list('question_id', 'id', "is_correct",'question__answer__question')
