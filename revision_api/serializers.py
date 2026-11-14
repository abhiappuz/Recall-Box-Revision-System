from rest_framework import serializers
from .models import RevisionSession, Question, AnswerAttempt, RevisionTopic, QuestionBank


# Serializer for Revision Session
class RevisionSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RevisionSession
        fields = '__all__'


# Serializer for Questions
class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = '__all__'


class AnswerAttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerAttempt
        fields = '__all__'


class RevisionTopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = RevisionTopic
        fields = '__all__'

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'