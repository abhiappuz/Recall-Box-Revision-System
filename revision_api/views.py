from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import (QuestionBankSerializer, RevisionSessionSerializer,QuestionSerializer,AnswerAttemptSerializer,RevisionTopicSerializer)
from .models import RevisionSession, Question, AnswerAttempt, RevisionTopic, QuestionBank
from django.utils import timezone
from django.db.models import Count, Avg, Q




@api_view(['POST'])
def start_revision_session(request):

    data = request.data

    serializer = RevisionSessionSerializer(data=data)

    if serializer.is_valid():
        session = serializer.save()

        return Response(
            {
                "message": "Revision session started successfully",
                "session": RevisionSessionSerializer(session).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
def save_questions(request):

    questions_data = request.data.get('questions', [])

    if not questions_data:
        return Response(
            {"error": "No questions provided"},
            status=status.HTTP_400_BAD_REQUEST
        )

    bank_id = request.data.get('bank_id')

    if not bank_id:
        return Response(
            {"error": "Question Bank ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    bank = QuestionBank.objects.filter(
        bank_id=bank_id
    ).first()

    if not bank:
        return Response(
            {"error": "Question Bank not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    for question in questions_data:
        question['bank'] = bank.bank_id

        if int(question.get('topic_id', 0)) != bank.topic_id:
            return Response(
                {"error": "Question topic does not match bank topic"},
                status=status.HTTP_400_BAD_REQUEST
            )

    serializer = QuestionSerializer(
        data=questions_data,
        many=True
    )

    if serializer.is_valid():

        with transaction.atomic():
            saved_questions = serializer.save()

        return Response(
            {
                "message": "Questions saved successfully",
                "total_questions": len(saved_questions),
                "questions": QuestionSerializer(
                    saved_questions,
                    many=True
                ).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


import re


@api_view(['GET'])
def get_questions(request):

    topic_id = request.query_params.get('topic_id')

    if not topic_id:
        return Response(
            {"error": "Topic ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    questions = Question.objects.filter(
        topic_id=topic_id,
        is_active=True
    ).order_by('question_id')

    unique_questions = []
    seen_questions = set()

    for question in questions:

        # Normalize question text
        normalized_text = re.sub(
            r'\s+',
            ' ',
            question.question_text.lower().strip()
        )

        # Remove punctuation for comparison
        normalized_text = re.sub(
            r'[^\w\s]',
            '',
            normalized_text
        )

        if normalized_text not in seen_questions:

            seen_questions.add(normalized_text)
            unique_questions.append(question)

    serializer = QuestionSerializer(
        unique_questions,
        many=True
    )

    return Response({
        "total_questions": len(unique_questions),
        "questions": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def save_answer_attempt(request):

    data = request.data.copy()

    session_id = data.get('session')
    question_id = data.get('question')
    selected_answer = data.get('selected_answer', '').strip()
    time_taken = data.get('time_taken')

    if not session_id or not question_id or not selected_answer:
        return Response(
            {"error": "Required answer details are missing"},
            status=status.HTTP_400_BAD_REQUEST
        )

    question = Question.objects.filter(
        question_id=question_id,
        is_active=True
    ).first()

    if not question:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    correct_answer = question.correct_answer.strip().upper()[0]
    selected = selected_answer.upper()[0]

    data['is_correct'] = selected == correct_answer

    serializer = AnswerAttemptSerializer(data=data)

    if serializer.is_valid():
        attempt = serializer.save()

        return Response(
            {
                "message": "Answer saved successfully",
                "is_correct": attempt.is_correct,
                "attempt": AnswerAttemptSerializer(attempt).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def complete_revision_session(request):

    session_id = request.data.get('session_id')

    if not session_id:
        return Response(
            {"error": "Session ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    session = RevisionSession.objects.filter(
        session_id=session_id
    ).first()

    if not session:
        return Response(
            {"error": "Revision session not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    session.status = 'COMPLETED'
    session.ended_at = timezone.now()
    session.save()

    # Calculate total session duration
    duration = session.ended_at - session.started_at
    total_seconds = int(duration.total_seconds())

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return Response(
        {
            "message": "Revision session completed successfully",
            "session_id": session.session_id,
            "status": session.status,
            "ended_at": session.ended_at,
            "total_seconds": total_seconds,
            "duration": f"{minutes} min {seconds} sec"
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def question_performance(request):
    user_id = request.query_params.get('user_id')
    question_id = request.query_params.get('question_id')

    if not user_id or not question_id:
        return Response(
            {"error": "User ID and Question ID are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    performance = AnswerAttempt.objects.filter(
        user_id=user_id,
        question_id=question_id
    ).aggregate(
        total_attempts=Count('attempt_id'),
        correct_attempts=Count(
            'attempt_id',
            filter=Q(is_correct=True)
        ),
        incorrect_attempts=Count(
            'attempt_id',
            filter=Q(is_correct=False)
        ),
        average_time=Avg('time_taken')
    )

    total = performance['total_attempts']

    accuracy = 0
    if total > 0:
        accuracy = round(
            (performance['correct_attempts'] / total) * 100, 2
        )

    return Response({
        "question_id": question_id,
        "total_attempts": total,
        "correct_attempts": performance['correct_attempts'],
        "incorrect_attempts": performance['incorrect_attempts'],
        "accuracy": accuracy,
        "average_time": round(performance['average_time'] or 0, 2)
    })


@api_view(['GET'])
def topic_performance(request):
    user_id = request.query_params.get('user_id')
    topic_id = request.query_params.get('topic_id')

    if not user_id or not topic_id:
        return Response(
            {"error": "User ID and Topic ID are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    performance = AnswerAttempt.objects.filter(
        user_id=user_id,
        question__topic_id=topic_id
    ).aggregate(
        total_attempts=Count('attempt_id'),
        correct_attempts=Count(
            'attempt_id',
            filter=Q(is_correct=True)
        ),
        incorrect_attempts=Count(
            'attempt_id',
            filter=Q(is_correct=False)
        ),
        average_time=Avg('time_taken')
    )

    total = performance['total_attempts']

    accuracy = 0
    if total > 0:
        accuracy = round(
            (performance['correct_attempts'] / total) * 100, 2
        )
    # Weak Topic Detection
    if total == 0:
        performance_level = "NOT_ATTEMPTED"
        priority = "NOT_AVAILABLE"

    elif accuracy < 50:
        performance_level = "WEAK"
        priority = "HIGH"

    elif accuracy < 75:
        performance_level = "AVERAGE"
        priority = "MEDIUM"

    else:
        performance_level = "STRONG"
        priority = "LOW"

    return Response({
        "topic_id": topic_id,
        "total_attempts": total,
        "correct_attempts": performance['correct_attempts'],
        "incorrect_attempts": performance['incorrect_attempts'],
        "accuracy": accuracy,
        "performance_level": performance_level,
        "revision_priority": priority,
        "average_time": round(performance['average_time'] or 0, 2)
    }, status=status.HTTP_200_OK)


# Add Subject and Topic
@api_view(['POST'])
def add_revision_topic(request):

    serializer = RevisionTopicSerializer(data=request.data)

    if serializer.is_valid():
        topic = serializer.save()

        return Response({
            "message": "Topic added successfully",
            "topic": RevisionTopicSerializer(topic).data
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Get Subjects
@api_view(['GET'])
def get_revision_subjects(request):

    user_id = request.query_params.get('user_id')

    subjects = RevisionTopic.objects.filter(
        user_id=user_id
    ).values_list(
        'subject_name', flat=True
    ).distinct()

    return Response({
        "subjects": list(subjects)
    })


# Get Topics
@api_view(['GET'])
def get_revision_topics(request):

    user_id = request.query_params.get('user_id')
    subject_name = request.query_params.get('subject_name')

    topics = RevisionTopic.objects.filter(
        user_id=user_id,
        subject_name=subject_name
    )

    serializer = RevisionTopicSerializer(topics, many=True)

    return Response({
        "topics": serializer.data
    })


# Delete Topic
@api_view(['DELETE'])
def delete_revision_topic(request, topic_id):

    topic = RevisionTopic.objects.filter(
        revision_topic_id=topic_id
    ).first()

    if not topic:
        return Response(
            {"error": "Topic not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    topic.delete()

    return Response({
        "message": "Topic deleted successfully"
    })


@api_view(['POST'])
def create_question_bank(request):

    topic_id = request.data.get('topic_id')
    bank_name = request.data.get('bank_name')

    if not topic_id or not bank_name:
        return Response(
            {"error": "Topic ID and bank name are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    topic = RevisionTopic.objects.filter(
        revision_topic_id=topic_id
    ).first()

    if not topic:
        return Response(
            {"error": "Topic not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    bank = QuestionBank.objects.create(
        topic_id=topic_id,
        bank_name=bank_name
    )

    return Response({
        "message": "Question bank created successfully",
        "bank": QuestionBankSerializer(bank).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_question_banks(request):

    topic_id = request.query_params.get('topic_id')

    if not topic_id:
        return Response(
            {"error": "Topic ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    banks = QuestionBank.objects.filter(
        topic_id=topic_id
    ).order_by('-uploaded_at')

    serializer = QuestionBankSerializer(
        banks,
        many=True
    )

    return Response({
        "total_banks": banks.count(),
        "banks": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_bank_questions(request):

    bank_id = request.query_params.get('bank_id')

    if not bank_id:
        return Response(
            {"error": "Bank ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    bank = QuestionBank.objects.filter(
        bank_id=bank_id
    ).first()

    if not bank:
        return Response(
            {"error": "Question bank not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    questions = Question.objects.filter(
        bank_id=bank_id,
        is_active=True
    ).order_by('question_id')

    serializer = QuestionSerializer(
        questions,
        many=True
    )

    return Response({
        "bank_name": bank.bank_name,
        "total_questions": questions.count(),
        "questions": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_question(request, question_id):

    question = Question.objects.filter(
        question_id=question_id
    ).first()

    if not question:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = QuestionSerializer(
        question,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response({
            "message": "Question updated successfully",
            "question": serializer.data
        })

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ---------------- REVISION HISTORY ----------------

@api_view(['GET'])
def revision_history(request):

    user_id = request.query_params.get('user_id')

    if not user_id:
        return Response(
            {"error": "User ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    sessions = RevisionSession.objects.filter(
        user_id=user_id
    ).order_by('-started_at')

    history = []

    for session in sessions:

        attempts = session.answer_attempts.all()

        total_questions = attempts.count()

        correct_answers = attempts.filter(
            is_correct=True
        ).count()

        incorrect_answers = total_questions - correct_answers

        accuracy = 0

        if total_questions > 0:
            accuracy = round(
                (correct_answers / total_questions) * 100, 1
            )

        # Get topic name
        topic = RevisionTopic.objects.filter(
            revision_topic_id=session.topic_id
        ).first()

        topic_name = topic.topic_name if topic else "Unknown Topic"

        # Calculate duration
        total_seconds = 0

        if session.ended_at:
            duration = session.ended_at - session.started_at
            total_seconds = int(duration.total_seconds())

        history.append({
            "session_id": session.session_id,
            "date": session.started_at,
            "revision_mode": session.session_mode,
            "topic_name": topic_name,
            "status": session.status,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "accuracy": accuracy,
            "total_seconds": total_seconds
        })

    return Response({
        "total_sessions": len(history),
        "history": history
    }, status=status.HTTP_200_OK)


# ---------------- REVISION SESSION DETAILS ----------------

@api_view(['GET'])
def revision_session_details(request):

    session_id = request.query_params.get('session_id')

    if not session_id:
        return Response(
            {"error": "Session ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    session = RevisionSession.objects.filter(
        session_id=session_id
    ).first()

    if not session:
        return Response(
            {"error": "Session not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    attempts = session.answer_attempts.select_related(
        'question'
    ).all().order_by('attempted_at')

    questions = []

    for attempt in attempts:

        question = attempt.question

        questions.append({
            "question_id": question.question_id,
            "question_text": question.question_text,
            "selected_answer": attempt.selected_answer,
            "correct_answer": question.correct_answer,
            "is_correct": attempt.is_correct,
            "time_taken": attempt.time_taken,
            "explanation": question.explanation
        })

    return Response({
        "session_id": session.session_id,
        "questions": questions,
        "total_questions": len(questions)
    }, status=status.HTTP_200_OK)