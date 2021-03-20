import itertools
import warnings

from django.db import transaction
from django.db.models import Q
from rest_framework import serializers, RemovedInDRF313Warning
from rest_framework.exceptions import ValidationError

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

    def validate_answers(self, data):
        answers_validators = [
            self.validate_questions_data_exists,
            self.validate_correlation,
        ]
        for validate in answers_validators:
            validate(data)
        return data

    # validate that each choice_id corresponds to question_id
    def validate_correlation(self, answer_data: dict, raise_exception=None):
        for question_id, choice_id in answer_data.items():
            if int(question_id) not in list(self.poll_d.values())[0]:
                detail_descr = "Question ID is not applicable for this Poll"
                raise serializers.ValidationError(detail_descr, code=400)

            else:
                if choice_id not in list(self.poll_d.values())[0][int(question_id)]:
                    detail_descr = "Invalid choice ID. Choice ID is not applicable for this Question ID"
                    raise serializers.ValidationError(detail_descr, code=400)

    # validate presence of choices_ids and questions_ids in a selected poll
    def validate_questions_data_exists(self, answer_data: dict, raise_exception=None):
        for poll_id, question_data in self.poll_d.items():
            integer_questions_ids = [int(i) for i in list(answer_data.keys())]

            status = False
            for question_id in integer_questions_ids:
                if question_id not in list(question_data.keys()):
                    status = True
                    break
            if status:
                detail_descr = "Question ID is not applicable for this Poll"
                raise serializers.ValidationError(detail_descr, code=400)

            status = False
            answers_integers_ids = list(answer_data.values())
            for answer_id in answers_integers_ids:
                if answer_id not in list(itertools.chain.from_iterable(question_data.values())):
                    status = True
                    break
            if status:
                detail_descr = "Choice ID is not applicable for this Poll"
                raise serializers.ValidationError(detail_descr, code=400)

        return answer_data

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
        """poll_d = represent: poll_id:{question_id: [choice_id]}"""
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
class SerializerFilter(serializers.ListSerializer):
    """ Serializer for filtering Answers depending on user instance """

    def to_representation(self, data):
        if "custom_serializer" not in self.context:
            data = data.filter(user=self.context["request"].user)
        else:
            data = data.filter(user=self.context["custom_serializer"]["user_id"])

        return super().to_representation(data)


class PollQuestionAnswerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PollQuestionAnswer
        fields = "__all__"
        list_serializer_class = SerializerFilter


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

    def get_results(self, poll_obj):
        """polls' questions amount"""
        total_q = poll_obj.questions.count()
        if "custom_serializer" in self.context:
            user_id = self.context["custom_context"]["user_id"]
        else:
            user_id = self.context["request"].user
        choices_status = (
            PollQuestionAnswer.objects.select_related("question")
                .filter(
                Q(question__choices__is_correct=True)
                & Q(question__poll_id=poll_obj.id)
                & Q(user_id=user_id)
            )
                .values("question__choices__id", "choice", "question__choices__is_correct")
                .distinct()
        )

        """ Assemble map of ids to check if user choice to questions are correct """
        correct_answers = 0
        for data_q in list(choices_status):
            if data_q["question__choices__id"] == data_q["choice"]:
                """if choice id is equal to the id indicated by a user
                Thus the answer to a question is correct"""
                correct_answers += 1

        if total_q != 0:
            return f"{(correct_answers / total_q) * 100:.2f}%"
        return f"{0.0}%"

    class Meta:
        model = Poll
        fields = "__all__"
