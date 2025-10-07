# ============= views.py =============

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from .models import (
    Unit, Theme, Topic, Exercise, Question, Answer, FillBlankAnswer,
    StudentProgress, ExerciseSubmission, QuestionResponse
)
import json


@login_required
def unit_detail(request, unit_id):
    """Renderiza uma unidade completa com todos os temas e tópicos"""
    unit = get_object_or_404(Unit, id=unit_id, is_active=True)
    
    # Busca ou cria o progresso do aluno
    progress, created = StudentProgress.objects.get_or_create(
        student=request.user,
        unit=unit
    )
    
    # Busca todos os temas e tópicos da unidade
    themes = unit.themes.filter(is_active=True).prefetch_related(
        'topics__vocabulary_items',
        'topics__grammar_contents__examples',
        'topics__exercises__questions__answers',
        'topics__dialogues__lines',
        'topics__example_boxes'
    )
    
    context = {
        'unit': unit,
        'themes': themes,
        'progress': progress,
    }
    
    return render(request, 'courses/unit_detail.html', context)


@login_required
def exercise_view(request, exercise_id):
    """Renderiza um exercício específico"""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    questions = exercise.questions.all().prefetch_related('answers', 'fill_blank_answer')
    
    context = {
        'exercise': exercise,
        'questions': questions,
    }
    
    return render(request, 'courses/exercise.html', context)


@login_required
def submit_exercise(request, exercise_id):
    """Processa a submissão de um exercício"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    data = json.loads(request.body)
    
    answers = data.get('answers', {})
    time_spent = data.get('time_spent', 0)
    
    # Calcula a pontuação
    total_score = 0
    max_score = 0
    responses = []
    
    for question in exercise.questions.all():
        max_score += question.points
        question_id = str(question.id)
        student_answer = answers.get(question_id, '')
        
        is_correct = False
        points_earned = 0
        
        if exercise.exercise_type == 'fill_blank':
            # Verifica resposta de preencher lacunas
            try:
                correct_answer_obj = question.fill_blank_answer
                correct = correct_answer_obj.correct_answer.strip()
                alternatives = [alt.strip() for alt in correct_answer_obj.alternative_answers.split(',') if alt.strip()]
                
                if not correct_answer_obj.case_sensitive:
                    student_answer = student_answer.lower()
                    correct = correct.lower()
                    alternatives = [alt.lower() for alt in alternatives]
                
                is_correct = student_answer == correct or student_answer in alternatives
                
            except FillBlankAnswer.DoesNotExist:
                pass
        
        elif exercise.exercise_type == 'multiple_choice':
            # Verifica resposta de múltipla escolha
            try:
                selected_answer = Answer.objects.get(id=int(student_answer))
                is_correct = selected_answer.is_correct
            except (Answer.DoesNotExist, ValueError):
                pass
        
        elif exercise.exercise_type == 'true_false':
            # Verifica verdadeiro/falso
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer:
                is_correct = student_answer.lower() == correct_answer.answer_text.lower()
        
        if is_correct:
            points_earned = question.points
            total_score += points_earned
        
        responses.append({
            'question': question,
            'student_answer': student_answer,
            'is_correct': is_correct,
            'points_earned': points_earned
        })
    
    # Cria a submissão
    submission = ExerciseSubmission.objects.create(
        student=request.user,
        exercise=exercise,
        score=total_score,
        max_score=max_score,
        time_spent=time_spent
    )
    
    # Salva as respostas individuais
    for response_data in responses:
        QuestionResponse.objects.create(
            submission=submission,
            question=response_data['question'],
            student_answer=response_data['student_answer'],
            is_correct=response_data['is_correct'],
            points_earned=response_data['points_earned']
        )
    
    # Atualiza o progresso do aluno
    unit = exercise.topic.theme.unit
    update_student_progress(request.user, unit)
    
    # Retorna o resultado
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    return JsonResponse({
        'success': True,
        'score': total_score,
        'max_score': max_score,
        'percentage': round(percentage, 2),
        'responses': [
            {
                'question_id': r['question'].id,
                'is_correct': r['is_correct'],
                'points_earned': r['points_earned'],
                'explanation': r['question'].explanation
            } for r in responses
        ]
    })


def update_student_progress(student, unit):
    """Atualiza o percentual de conclusão da unidade"""
    progress, created = StudentProgress.objects.get_or_create(
        student=student,
        unit=unit
    )
    
    # Conta total de exercícios na unidade
    total_exercises = Exercise.objects.filter(
        topic__theme__unit=unit
    ).count()
    
    if total_exercises == 0:
        return
    
    # Conta exercícios completados
    completed_exercises = ExerciseSubmission.objects.filter(
        student=student,
        exercise__topic__theme__unit=unit
    ).values('exercise').distinct().count()
    
    # Calcula o percentual
    percentage = int((completed_exercises / total_exercises) * 100)
    progress.completion_percentage = percentage
    
    # Se completou 100%, marca a data
    if percentage == 100 and not progress.completed_at:
        progress.completed_at = timezone.now()
    
    progress.save()


@login_required
def student_dashboard(request):
    """Dashboard do aluno com seu progresso"""
    progress_list = StudentProgress.objects.filter(
        student=request.user
    ).select_related('unit').order_by('-started_at')
    
    # Estatísticas gerais
    total_units = Unit.objects.filter(is_active=True).count()
    completed_units = progress_list.filter(completion_percentage=100).count()
    
    submissions = ExerciseSubmission.objects.filter(student=request.user)
    avg_score = submissions.aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'progress_list': progress_list,
        'total_units': total_units,
        'completed_units': completed_units,
        'avg_score': round(avg_score, 2),
        'total_exercises': submissions.count(),
    }
    
    return render(request, 'courses/dashboard.html', context)


# ============= unit_detail.html (Template) =============
"""
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ unit.title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .progress-bar {
            background: rgba(255,255,255,0.2);
            height: 10px;
            border-radius: 5px;
            margin: 20px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            background: white;
            height: 100%;
            width: {{ progress.completion_percentage }}%;
            transition: width 0.3s ease;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }
        
        .section-title {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .topic {
            background: #f8f9fa;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .topic:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .topic-header {
            color: #764ba2;
            font-size: 1.3em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .vocabulary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .vocab-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            text-align: center;
        }
        
        .vocab-word {
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        
        .vocab-translation {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .example-box {
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        
        .example-box.example {
            background: #fff3cd;
            border-color: #ffc107;
        }
        
        .example-box.tip {
            background: #d1ecf1;
            border-color: #17a2b8;
        }
        
        .example-box.warning {
            background: #f8d7da;
            border-color: #dc3545;
        }
        
        .example-box.info {
            background: #d1ecf1;
            border-color: #17a2b8;
        }
        
        .grammar-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .grammar-table th,
        .grammar-table td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        
        .grammar-table th {
            background: #667eea;
            color: white;
        }
        
        .grammar-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .exercise-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 25px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 15px;
            transition: background 0.3s ease;
        }
        
        .exercise-link:hover {
            background: #764ba2;
        }
        
        .dialogue-line {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        
        .dialogue-speaker {
            font-weight: bold;
            color: #667eea;
        }
        
        .dialogue-translation {
            color: #6c757d;
            font-size: 0.9em;
            font-style: italic;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ unit.icon }} {{ unit.title }}</h1>
            <p>{{ unit.description }}</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <small>{{ progress.completion_percentage }}% Complete</small>
        </div>
        
        <div class="content">
            {% for theme in themes %}
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">{{ theme.icon }}</span> {{ theme.title }}
                </h2>
                
                {% for topic in theme.topics.all %}
                <div class="topic">
                    <h3 class="topic-header">{{ topic.icon }} {{ topic.title }}</h3>
                    
                    {% if topic.description %}
                    <p>{{ topic.description }}</p>
                    {% endif %}
                    
                    <!-- VOCABULARY -->
                    {% if topic.topic_type == 'vocabulary' and topic.vocabulary_items.all %}
                    <div class="vocabulary-grid">
                        {% for item in topic.vocabulary_items.all %}
                        <div class="vocab-item">
                            {% if item.image %}
                            <img src="{{ item.image.url }}" alt="{{ item.word }}" style="width:100%; max-height:100px; object-fit:cover; border-radius:5px; margin-bottom:10px;">
                            {% endif %}
                            <div class="vocab-word">{{ item.word }}</div>
                            <div class="vocab-translation">{{ item.translation }}</div>
                            {% if item.pronunciation %}
                            <div style="color: #999; font-size:0.8em; margin-top:3px;">/{{ item.pronunciation }}/</div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    <!-- GRAMMAR -->
                    {% if topic.topic_type == 'grammar' and topic.grammar_contents.all %}
                        {% for grammar in topic.grammar_contents.all %}
                        <h4 style="margin-top:20px; color:#764ba2;">{{ grammar.title }}</h4>
                        <p>{{ grammar.explanation }}</p>
                        
                        {% if grammar.examples.all %}
                        <table class="grammar-table">
                            <thead>
                                <tr>
                                    <th>Subject</th>
                                    <th>Verb Form</th>
                                    <th>Example</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for example in grammar.examples.all %}
                                <tr>
                                    <td>{{ example.subject }}</td>
                                    <td>{{ example.verb_form }}</td>
                                    <td>{{ example.example_sentence }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                        {% endif %}
                        {% endfor %}
                    {% endif %}
                    
                    <!-- DIALOGUES (Speaking) -->
                    {% if topic.topic_type == 'speaking' and topic.dialogues.all %}
                        {% for dialogue in topic.dialogues.all %}
                        <h4 style="margin-top:20px; color:#764ba2;">{{ dialogue.title }}</h4>
                        {% if dialogue.context %}
                        <p><em>{{ dialogue.context }}</em></p>
                        {% endif %}
                        
                        {% for line in dialogue.lines.all %}
                        <div class="dialogue-line">
                            <div class="dialogue-speaker">{{ line.speaker }}:</div>
                            <div>{{ line.text }}</div>
                            {% if line.translation %}
                            <div class="dialogue-translation">{{ line.translation }}</div>
                            {% endif %}
                        </div>
                        {% endfor %}
                        {% endfor %}
                    {% endif %}
                    
                    <!-- EXAMPLE BOXES -->
                    {% for example in topic.example_boxes.all %}
                    <div class="example-box {{ example.box_type }}">
                        <strong>{{ example.title }}:</strong><br>
                        {{ example.content|linebreaks }}
                    </div>
                    {% endfor %}
                    
                    <!-- EXERCISES -->
                    {% if topic.exercises.all %}
                    <div style="margin-top:20px;">
                        <strong>📝 Exercises:</strong><br>
                        {% for exercise in topic.exercises.all %}
                        <a href="{% url 'exercise_view' exercise.id %}" class="exercise-link">
                            {{ exercise.title }} ({{ exercise.questions.count }} questions)
                        </a>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""