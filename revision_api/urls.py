from django.urls import path
from . import views

urlpatterns = [
    # Revision Session
    path('start-session/', views.start_revision_session, name='start_revision_session'),
    path('complete-session/', views.complete_revision_session, name='complete_revision_session'),
    path('revision-history/', views.revision_history, name='revision_history'),
    path('session-details/',views.revision_session_details,name='revision_session_details'),
    

    # Question Management
    path('save-questions/', views.save_questions, name='save_questions'),
    path('get-questions/', views.get_questions, name='get_questions'),

    # Answer Management
    path('save-answer/', views.save_answer_attempt, name='save_answer_attempt'),

    # Performance Analysis
    path('question-performance/', views.question_performance, name='question_performance'),
    path('topic-performance/', views.topic_performance, name='topic_performance'),

    # Revision Subject and Topic Management
    path('add-topic/', views.add_revision_topic, name='add_revision_topic'),
    path('get-subjects/', views.get_revision_subjects, name='get_revision_subjects'),
    path('get-topics/', views.get_revision_topics, name='get_revision_topics'),
    path('delete-topic/<int:topic_id>/', views.delete_revision_topic, name='delete_revision_topic'),
    path('create-bank/',views.create_question_bank,name='create_question_bank'),
    path('get-banks/',views.get_question_banks,name='get_question_banks'),
    path('get-bank-questions/',views.get_bank_questions,name='get_bank_questions'),
    path('update-question/<int:question_id>/',views.update_question,name='update_question'),
]