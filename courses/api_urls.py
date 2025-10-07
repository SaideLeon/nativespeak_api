from django.urls import path, include
from rest_framework.routers import DefaultRouter 

from .api_views import (
    UnitViewSet, ThemeViewSet, TopicViewSet, ExerciseViewSet,
    StudentProgressViewSet, ExerciseSubmissionViewSet, DashboardViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'progress', StudentProgressViewSet, basename='progress')
router.register(r'submissions', ExerciseSubmissionViewSet, basename='submission')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [ 
    # API Routes
    path('', include(router.urls)),
]

"""
=============================================================================
📚 DOCUMENTAÇÃO DA API
============================================================================= 
📖 UNITS (Unidades)
-------------------
GET /api/units/
    Lista todas as unidades (resumida)
    Query params: -
    Returns: [
        {
            "id": 1,
            "number": 3,
            "title": "Daily Life",
            "description": "...",
            "icon": "📚",
            "order": 3,
            "theme_count": 2
        }
    ]

GET /api/units/{id}/
    Detalhes completos de uma unidade (com todos os temas, tópicos e conteúdo)
    Returns: {
        "id": 1,
        "number": 3,
        "title": "Daily Life",
        "themes": [
            {
                "id": 1,
                "title": "Food and Eating Habits",
                "icon": "🍽️",
                "topics": [
                    {
                        "id": 1,
                        "title": "Types of Food",
                        "topic_type": "vocabulary",
                        "vocabulary_items": [...],
                        "grammar_contents": [],
                        "dialogues": [],
                        "example_boxes": [...],
                        "exercises": [...]
                    }
                ]
            }
        ]
    }

GET /api/units/{id}/progress/ (🔐 autenticado)
    Progresso do aluno na unidade
    Returns: {
        "id": 1,
        "unit": {...},
        "completion_percentage": 66,
        "started_at": "2025-01-15T10:00:00Z",
        "completed_at": null
    }


🎨 THEMES (Temas)
-----------------
GET /api/themes/
    Lista todos os temas
    Query params: ?unit={unit_id}
    Returns: [{...}]

GET /api/themes/{id}/
    Detalhes de um tema com todos os tópicos


📝 TOPICS (Tópicos)
-------------------
GET /api/topics/
    Lista todos os tópicos
    Query params: 
        ?theme={theme_id}
        ?type={vocabulary|grammar|speaking|reading|writing|listening}
    Returns: [{...}]

GET /api/topics/{id}/
    Detalhes completos de um tópico com todo o conteúdo


✏️ EXERCISES (Exercícios)
-------------------------
GET /api/exercises/
    Lista todos os exercícios
    Query params:
        ?topic={topic_id}
        ?type={fill_blank|multiple_choice|true_false}
    Returns: [
        {
            "id": 1,
            "title": "Complete the sentences",
            "exercise_type": "fill_blank",
            "exercise_type_display": "Fill in the Blanks",
            "instructions": "...",
            "points": 30,
            "question_count": 3,
            "questions": [...]
        }
    ]

GET /api/exercises/{id}/
    Detalhes de um exercício com todas as questões
    Returns: {
        "id": 1,
        "questions": [
            {
                "id": 1,
                "question_text": "I _____ (eat) breakfast.",
                "hint": "Use simple present for I",
                "explanation": "We use 'eat' for I/You/We/They",
                "points": 10,
                "fill_blank_answer": {
                    "correct_answer": "eat",
                    "alternative_answers": "",
                    "case_sensitive": false
                }
            }
        ]
    }

POST /api/exercises/{id}/submit/ (🔐 autenticado)
    Submeter respostas de um exercício
    Body: {
        "answers": {
            "1": "eat",
            "2": "drinks",
            "3": "have"
        },
        "time_spent": 120
    }
    Returns: {
        "success": true,
        "submission_id": 1,
        "score": 20,
        "max_score": 30,
        "percentage": 66.67,
        "responses": [
            {
                "question_id": 1,
                "is_correct": true,
                "points_earned": 10,
                "explanation": "...",
                "correct_answer": "eat"
            },
            {
                "question_id": 2,
                "is_correct": true,
                "points_earned": 10,
                "explanation": "...",
                "correct_answer": "drinks"
            },
            {
                "question_id": 3,
                "is_correct": false,
                "points_earned": 0,
                "explanation": "...",
                "correct_answer": "have"
            }
        ]
    }


📊 PROGRESS (Progresso)
-----------------------
GET /api/progress/ (🔐 autenticado)
    Lista todo o progresso do aluno
    Returns: [
        {
            "id": 1,
            "unit": {
                "id": 1,
                "number": 3,
                "title": "Daily Life",
                "icon": "📚"
            },
            "completion_percentage": 66,
            "started_at": "2025-01-15T10:00:00Z",
            "completed_at": null
        }
    ]

GET /api/progress/{id}/ (🔐 autenticado)
    Detalhes de um progresso específico


📋 SUBMISSIONS (Submissões)
---------------------------
GET /api/submissions/ (🔐 autenticado)
    Lista todas as submissões do aluno
    Query params:
        ?exercise={exercise_id}
        ?unit={unit_id}
    Returns: [
        {
            "id": 1,
            "exercise": {...},
            "score": 20,
            "max_score": 30,
            "percentage": 66.67,
            "submitted_at": "2025-01-15T11:00:00Z",
            "time_spent": 120,
            "responses": [...]
        }
    ]

GET /api/submissions/{id}/ (🔐 autenticado)
    Detalhes de uma submissão específica


📈 DASHBOARD
------------
GET /api/dashboard/ (🔐 autenticado)
    Estatísticas completas do aluno
    Returns: {
        "total_units": 10,
        "completed_units": 3,
        "in_progress_units": 2,
        "total_exercises": 45,
        "avg_score": 78.5,
        "exercise_stats": {
            "fill_blank": {
                "count": 20,
                "avg_score": 80.0
            },
            "multiple_choice": {
                "count": 15,
                "avg_score": 75.0
            },
            "true_false": {
                "count": 10,
                "avg_score": 82.0
            }
        },
        "recent_progress": [...],
        "recent_submissions": [...]
    }


=============================================================================
💡 EXEMPLOS DE USO NO REACT
=============================================================================

// 1. Login e obter token
const login = async (username, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
};

// 2. Buscar todas as unidades
const getUnits = async () => {
    const response = await fetch('http://localhost:8000/api/units/');
    return await response.json();
};

// 3. Buscar uma unidade completa
const getUnitDetail = async (unitId) => {
    const response = await fetch(`http://localhost:8000/api/units/${unitId}/`);
    return await response.json();
};

// 4. Submeter um exercício (com autenticação)
const submitExercise = async (exerciseId, answers, timeSpent) => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(
        `http://localhost:8000/api/exercises/${exerciseId}/submit/`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                answers: answers,
                time_spent: timeSpent
            })
        }
    );
    return await response.json();
};

// 5. Buscar dashboard
const getDashboard = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://localhost:8000/api/dashboard/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
};

=============================================================================
"""