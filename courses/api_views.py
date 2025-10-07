from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Unit, Theme, Topic, Exercise, Question, Answer, FillBlankAnswer,
    StudentProgress, ExerciseSubmission, QuestionResponse
)
from .serializers import (
    UnitSerializer, UnitListSerializer, ThemeSerializer, TopicSerializer,
    ExerciseSerializer, StudentProgressSerializer, ExerciseSubmissionSerializer,
    ExerciseSubmissionCreateSerializer, StudentDashboardSerializer
)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Units
    
    list: GET /api/units/ - Lista todas as unidades
    retrieve: GET /api/units/{id}/ - Detalhes de uma unidade com todos os temas e tópicos
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Unit.objects.filter(is_active=True).prefetch_related(
            'themes__topics__vocabulary_items',
            'themes__topics__grammar_contents__examples',
            'themes__topics__dialogues__lines',
            'themes__topics__example_boxes',
            'themes__topics__exercises__questions__answers',
        ).order_by('order', 'number')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UnitListSerializer
        return UnitSerializer
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def progress(self, request, pk=None):
        """
        GET /api/units/{id}/progress/
        Retorna o progresso do aluno na unidade
        """
        unit = self.get_object()
        progress, created = StudentProgress.objects.get_or_create(
            student=request.user,
            unit=unit
        )
        serializer = StudentProgressSerializer(progress)
        return Response(serializer.data)


class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Themes
    
    list: GET /api/themes/ - Lista todos os temas
    retrieve: GET /api/themes/{id}/ - Detalhes de um tema
    """
    permission_classes = [AllowAny]
    serializer_class = ThemeSerializer
    
    def get_queryset(self):
        queryset = Theme.objects.filter(is_active=True).prefetch_related(
            'topics__vocabulary_items',
            'topics__grammar_contents__examples',
            'topics__dialogues__lines',
            'topics__example_boxes',
            'topics__exercises__questions',
        ).order_by('unit__order', 'order')
        
        # Filtrar por unit se fornecido
        unit_id = self.request.query_params.get('unit')
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        return queryset


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Topics
    
    list: GET /api/topics/ - Lista todos os tópicos
    retrieve: GET /api/topics/{id}/ - Detalhes de um tópico
    """
    permission_classes = [AllowAny]
    serializer_class = TopicSerializer
    
    def get_queryset(self):
        queryset = Topic.objects.filter(is_active=True).prefetch_related(
            'vocabulary_items',
            'grammar_contents__examples',
            'dialogues__lines',
            'example_boxes',
            'exercises__questions__answers',
            'exercises__questions__fill_blank_answer',
        ).order_by('theme__order', 'order')
        
        # Filtros opcionais
        theme_id = self.request.query_params.get('theme')
        topic_type = self.request.query_params.get('type')
        
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        if topic_type:
            queryset = queryset.filter(topic_type=topic_type)
        
        return queryset


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Exercises
    
    list: GET /api/exercises/ - Lista todos os exercícios
    retrieve: GET /api/exercises/{id}/ - Detalhes de um exercício
    submit: POST /api/exercises/{id}/submit/ - Submeter respostas
    """
    permission_classes = [AllowAny]
    serializer_class = ExerciseSerializer
    
    def get_queryset(self):
        queryset = Exercise.objects.all().prefetch_related(
            'questions__answers',
            'questions__fill_blank_answer',
        ).order_by('topic__theme__unit__order', 'order')
        
        # Filtros opcionais
        topic_id = self.request.query_params.get('topic')
        exercise_type = self.request.query_params.get('type')
        
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """
        POST /api/exercises/{id}/submit/
        Body: {
            "answers": {"question_id": "answer", ...},
            "time_spent": 120
        }
        
        Retorna: {
            "success": true,
            "score": 80,
            "max_score": 100,
            "percentage": 80.0,
            "responses": [...]
        }
        """
        exercise = self.get_object()
        
        # Validar dados de entrada
        input_serializer = ExerciseSubmissionCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        answers = input_serializer.validated_data['answers']
        time_spent = input_serializer.validated_data.get('time_spent', 0)
        
        # Processar respostas
        total_score = 0
        max_score = 0
        responses = []
        
        for question in exercise.questions.all():
            max_score += question.points
            question_id = str(question.id)
            student_answer = answers.get(question_id, '')
            
            is_correct = False
            points_earned = 0
            
            # Verificar resposta baseado no tipo de exercício
            if exercise.exercise_type == 'fill_blank':
                is_correct = self._check_fill_blank(question, student_answer)
            
            elif exercise.exercise_type == 'multiple_choice':
                is_correct = self._check_multiple_choice(question, student_answer)
            
            elif exercise.exercise_type == 'true_false':
                is_correct = self._check_true_false(question, student_answer)
            
            if is_correct:
                points_earned = question.points
                total_score += points_earned
            
            responses.append({
                'question': question,
                'student_answer': student_answer,
                'is_correct': is_correct,
                'points_earned': points_earned
            })
        
        # Criar submissão
        submission = ExerciseSubmission.objects.create(
            student=request.user,
            exercise=exercise,
            score=total_score,
            max_score=max_score,
            time_spent=time_spent
        )
        
        # Salvar respostas individuais
        for response_data in responses:
            QuestionResponse.objects.create(
                submission=submission,
                question=response_data['question'],
                student_answer=response_data['student_answer'],
                is_correct=response_data['is_correct'],
                points_earned=response_data['points_earned']
            )
        
        # Atualizar progresso
        self._update_progress(request.user, exercise)
        
        # Retornar resultado
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return Response({
            'success': True,
            'submission_id': submission.id,
            'score': total_score,
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'responses': [
                {
                    'question_id': r['question'].id,
                    'is_correct': r['is_correct'],
                    'points_earned': r['points_earned'],
                    'explanation': r['question'].explanation,
                    'correct_answer': self._get_correct_answer(r['question'], exercise.exercise_type)
                } for r in responses
            ]
        })
    
    def _check_fill_blank(self, question, student_answer):
        """Verifica resposta de preencher lacunas"""
        try:
            correct_answer_obj = question.fill_blank_answer
            correct = correct_answer_obj.correct_answer.strip()
            alternatives = [
                alt.strip() 
                for alt in correct_answer_obj.alternative_answers.split(',') 
                if alt.strip()
            ]
            
            if not correct_answer_obj.case_sensitive:
                student_answer = student_answer.lower()
                correct = correct.lower()
                alternatives = [alt.lower() for alt in alternatives]
            
            return student_answer == correct or student_answer in alternatives
        except FillBlankAnswer.DoesNotExist:
            return False
    
    def _check_multiple_choice(self, question, student_answer):
        """Verifica resposta de múltipla escolha"""
        try:
            selected_answer = Answer.objects.get(id=int(student_answer))
            return selected_answer.is_correct
        except (Answer.DoesNotExist, ValueError):
            return False
    
    def _check_true_false(self, question, student_answer):
        """Verifica resposta de verdadeiro/falso"""
        correct_answer = question.answers.filter(is_correct=True).first()
        if correct_answer:
            return student_answer.lower() == correct_answer.answer_text.lower()
        return False
    
    def _get_correct_answer(self, question, exercise_type):
        """Retorna a resposta correta formatada"""
        if exercise_type == 'fill_blank':
            try:
                return question.fill_blank_answer.correct_answer
            except FillBlankAnswer.DoesNotExist:
                return None
        elif exercise_type in ['multiple_choice', 'true_false']:
            correct = question.answers.filter(is_correct=True).first()
            return correct.answer_text if correct else None
        return None
    
    def _update_progress(self, student, exercise):
        """Atualiza o progresso do aluno"""
        unit = exercise.topic.theme.unit
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
        
        # Calcula percentual
        percentage = int((completed_exercises / total_exercises) * 100)
        progress.completion_percentage = percentage
        
        # Se completou 100%, marca a data
        if percentage == 100 and not progress.completed_at:
            progress.completed_at = timezone.now()
        
        progress.save()


class StudentProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Student Progress
    
    list: GET /api/progress/ - Progresso em todas as unidades
    retrieve: GET /api/progress/{id}/ - Detalhes de progresso específico
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProgressSerializer
    
    def get_queryset(self):
        return StudentProgress.objects.filter(
            student=self.request.user
        ).select_related('unit').order_by('-started_at')


class ExerciseSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para Exercise Submissions
    
    list: GET /api/submissions/ - Lista todas as submissões do aluno
    retrieve: GET /api/submissions/{id}/ - Detalhes de uma submissão
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseSubmissionSerializer
    
    def get_queryset(self):
        queryset = ExerciseSubmission.objects.filter(
            student=self.request.user
        ).select_related(
            'exercise__topic__theme__unit'
        ).prefetch_related(
            'responses__question'
        ).order_by('-submitted_at')
        
        # Filtros opcionais
        exercise_id = self.request.query_params.get('exercise')
        unit_id = self.request.query_params.get('unit')
        
        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)
        if unit_id:
            queryset = queryset.filter(exercise__topic__theme__unit_id=unit_id)
        
        return queryset


class DashboardViewSet(viewsets.ViewSet):
    """
    API endpoint para Dashboard do Aluno
    
    GET /api/dashboard/ - Retorna todas as estatísticas do aluno
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        GET /api/dashboard/
        Retorna estatísticas completas do aluno
        """
        student = request.user
        
        # Estatísticas de unidades
        total_units = Unit.objects.filter(is_active=True).count()
        progress_list = StudentProgress.objects.filter(student=student)
        completed_units = progress_list.filter(completion_percentage=100).count()
        in_progress_units = progress_list.filter(
            completion_percentage__gt=0, 
            completion_percentage__lt=100
        ).count()
        
        # Estatísticas de exercícios
        submissions = ExerciseSubmission.objects.filter(student=student)
        total_exercises = submissions.count()
        avg_score = submissions.aggregate(Avg('score'))['score__avg'] or 0
        
        # Estatísticas por tipo de exercício
        exercise_stats = {}
        for ex_type in ['fill_blank', 'multiple_choice', 'true_false']:
            type_submissions = submissions.filter(exercise__exercise_type=ex_type)
            exercise_stats[ex_type] = {
                'count': type_submissions.count(),
                'avg_score': type_submissions.aggregate(Avg('score'))['score__avg'] or 0
            }
        
        # Progresso recente
        recent_progress = progress_list.order_by('-started_at')[:5]
        
        # Submissões recentes
        recent_submissions = submissions.order_by('-submitted_at')[:10]
        
        data = {
            'total_units': total_units,
            'completed_units': completed_units,
            'in_progress_units': in_progress_units,
            'total_exercises': total_exercises,
            'avg_score': round(avg_score, 2),
            'exercise_stats': exercise_stats,
            'recent_progress': StudentProgressSerializer(recent_progress, many=True).data,
            'recent_submissions': ExerciseSubmissionSerializer(recent_submissions, many=True).data,
        }
        
        serializer = StudentDashboardSerializer(data)
        return Response(serializer.data)