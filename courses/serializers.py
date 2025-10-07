from rest_framework import serializers
from .models import (
    Unit, Theme, Topic, VocabularyItem, GrammarContent, GrammarExample,
    Exercise, Question, Answer, FillBlankAnswer, DialogueContent, DialogueLine,
    ExampleBox, StudentProgress, ExerciseSubmission, QuestionResponse
)


# ============= NESTED SERIALIZERS =============

class VocabularyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyItem
        fields = [
            'id', 'word', 'translation', 'pronunciation', 
            'image', 'audio', 'example_sentence', 'order'
        ]


class GrammarExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExample
        fields = [
            'id', 'subject', 'verb_form', 'example_sentence', 
            'translation', 'order'
        ]


class GrammarContentSerializer(serializers.ModelSerializer):
    examples = GrammarExampleSerializer(many=True, read_only=True)
    
    class Meta:
        model = GrammarContent
        fields = ['id', 'title', 'explanation', 'examples', 'order']


class DialogueLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DialogueLine
        fields = ['id', 'speaker', 'text', 'translation', 'audio', 'order']


class DialogueContentSerializer(serializers.ModelSerializer):
    lines = DialogueLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = DialogueContent
        fields = ['id', 'title', 'context', 'lines', 'order']


class ExampleBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleBox
        fields = ['id', 'title', 'content', 'box_type', 'order']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']


class FillBlankAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillBlankAnswer
        fields = ['id', 'correct_answer', 'alternative_answers', 'case_sensitive']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    fill_blank_answer = FillBlankAnswerSerializer(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'hint', 'explanation', 
            'order', 'points', 'answers', 'fill_blank_answer'
        ]


class ExerciseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    exercise_type_display = serializers.CharField(source='get_exercise_type_display', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'exercise_type', 'exercise_type_display',
            'instructions', 'order', 'points', 'questions', 'question_count'
        ]
    
    def get_question_count(self, obj):
        return obj.questions.count()


# ============= TOPIC SERIALIZER (MAIN) =============

class TopicSerializer(serializers.ModelSerializer):
    # Conteúdos condicionais baseados no tipo
    vocabulary_items = VocabularyItemSerializer(many=True, read_only=True)
    grammar_contents = GrammarContentSerializer(many=True, read_only=True)
    dialogues = DialogueContentSerializer(many=True, read_only=True)
    example_boxes = ExampleBoxSerializer(many=True, read_only=True)
    exercises = ExerciseSerializer(many=True, read_only=True)
    
    topic_type_display = serializers.CharField(source='get_topic_type_display', read_only=True)
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'topic_type', 'topic_type_display', 'icon',
            'description', 'order', 'vocabulary_items', 'grammar_contents',
            'dialogues', 'example_boxes', 'exercises'
        ]


class TopicListSerializer(serializers.ModelSerializer):
    """Versão simplificada para listagem (sem conteúdo completo)"""
    topic_type_display = serializers.CharField(source='get_topic_type_display', read_only=True)
    content_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'topic_type', 'topic_type_display', 
            'icon', 'order', 'content_summary'
        ]
    
    def get_content_summary(self, obj):
        return {
            'vocabulary_count': obj.vocabulary_items.count(),
            'grammar_count': obj.grammar_contents.count(),
            'dialogue_count': obj.dialogues.count(),
            'exercise_count': obj.exercises.count(),
        }


# ============= THEME SERIALIZER =============

class ThemeSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Theme
        fields = ['id', 'title', 'icon', 'order', 'topics', 'topic_count']
    
    def get_topic_count(self, obj):
        return obj.topics.filter(is_active=True).count()


class ThemeListSerializer(serializers.ModelSerializer):
    """Versão simplificada sem os tópicos completos"""
    topics = TopicListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Theme
        fields = ['id', 'title', 'icon', 'order', 'topics']


# ============= UNIT SERIALIZER =============

class UnitSerializer(serializers.ModelSerializer):
    themes = ThemeSerializer(many=True, read_only=True)
    theme_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'number', 'title', 'description', 'icon', 
            'order', 'themes', 'theme_count'
        ]
    
    def get_theme_count(self, obj):
        return obj.themes.filter(is_active=True).count()


class UnitListSerializer(serializers.ModelSerializer):
    """Versão simplificada para listagem de unidades"""
    theme_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'number', 'title', 'description', 
            'icon', 'order', 'theme_count'
        ]
    
    def get_theme_count(self, obj):
        return obj.themes.filter(is_active=True).count()


# ============= PROGRESS SERIALIZERS =============

class StudentProgressSerializer(serializers.ModelSerializer):
    unit = UnitListSerializer(read_only=True)
    unit_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'unit', 'unit_id', 'completion_percentage',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['completion_percentage', 'started_at', 'completed_at']


class QuestionResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'question', 'student_answer', 
            'is_correct', 'points_earned'
        ]


class ExerciseSubmissionSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    responses = QuestionResponseSerializer(many=True, read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ExerciseSubmission
        fields = [
            'id', 'exercise', 'score', 'max_score', 'percentage',
            'submitted_at', 'time_spent', 'responses'
        ]
    
    def get_percentage(self, obj):
        if obj.max_score > 0:
            return round((obj.score / obj.max_score) * 100, 2)
        return 0


class ExerciseSubmissionCreateSerializer(serializers.Serializer):
    """Serializer para criar uma submissão de exercício"""
    exercise_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text="Objeto com question_id como chave e resposta como valor"
    )
    time_spent = serializers.IntegerField(
        required=False, 
        help_text="Tempo gasto em segundos"
    )
    
    def validate_exercise_id(self, value):
        try:
            Exercise.objects.get(id=value)
        except Exercise.DoesNotExist:
            raise serializers.ValidationError("Exercise not found")
        return value


# ============= DASHBOARD SERIALIZER =============

class StudentDashboardSerializer(serializers.Serializer):
    """Serializer para dados do dashboard do aluno"""
    total_units = serializers.IntegerField()
    completed_units = serializers.IntegerField()
    in_progress_units = serializers.IntegerField()
    total_exercises = serializers.IntegerField()
    avg_score = serializers.FloatField()
    recent_progress = StudentProgressSerializer(many=True)
    recent_submissions = ExerciseSubmissionSerializer(many=True)
    
    # Estatísticas por tipo de exercício
    exercise_stats = serializers.DictField()


# ============= MINIMAL SERIALIZERS (para performance) =============

class UnitMinimalSerializer(serializers.ModelSerializer):
    """Apenas informações básicas da unidade"""
    class Meta:
        model = Unit
        fields = ['id', 'number', 'title', 'icon']


class ThemeMinimalSerializer(serializers.ModelSerializer):
    """Apenas informações básicas do tema"""
    class Meta:
        model = Theme
        fields = ['id', 'title', 'icon', 'order']


class TopicMinimalSerializer(serializers.ModelSerializer):
    """Apenas informações básicas do tópico"""
    class Meta:
        model = Topic
        fields = ['id', 'title', 'topic_type', 'icon', 'order']