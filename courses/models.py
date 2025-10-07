from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Unit(models.Model):
    """Unidade do curso (ex: Unit 3: Daily Life)"""
    title = models.CharField(max_length=200)
    number = models.IntegerField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="📚", help_text="Emoji ou ícone")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'number']
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
    
    def __str__(self):
        return f"Unit {self.number}: {self.title}"


class Theme(models.Model):
    """Tema dentro de uma unidade (ex: Food and Eating Habits)"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='themes')
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default="🎯")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
    
    def __str__(self):
        return f"{self.unit.title} - {self.title}"


class Topic(models.Model):
    """Tópico dentro de um tema (ex: Vocabulary, Grammar, Speaking)"""
    TOPIC_TYPES = [
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('pronunciation', 'Pronunciation'),
    ]
    
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    topic_type = models.CharField(max_length=20, choices=TOPIC_TYPES)
    icon = models.CharField(max_length=50, default="📝")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
    
    def __str__(self):
        return f"{self.theme.title} - {self.title}"


class VocabularyItem(models.Model):
    """Item de vocabulário"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='vocabulary_items')
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    pronunciation = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='vocabulary/', blank=True, null=True)
    audio = models.FileField(upload_to='audio/vocabulary/', blank=True, null=True)
    example_sentence = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Vocabulary Item'
        verbose_name_plural = 'Vocabulary Items'
    
    def __str__(self):
        return f"{self.word} - {self.translation}"


class GrammarContent(models.Model):
    """Conteúdo gramatical"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='grammar_contents')
    title = models.CharField(max_length=200)
    explanation = models.TextField(help_text="Explicação da regra gramatical")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Grammar Content'
        verbose_name_plural = 'Grammar Contents'
    
    def __str__(self):
        return self.title


class GrammarExample(models.Model):
    """Exemplos gramaticais"""
    grammar_content = models.ForeignKey(GrammarContent, on_delete=models.CASCADE, related_name='examples')
    subject = models.CharField(max_length=100, blank=True)
    verb_form = models.CharField(max_length=100, blank=True)
    example_sentence = models.TextField()
    translation = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.example_sentence[:50]


class Exercise(models.Model):
    """Exercício de qualquer tipo"""
    EXERCISE_TYPES = [
        ('fill_blank', 'Fill in the Blanks'),
        ('multiple_choice', 'Multiple Choice'),
        ('matching', 'Matching'),
        ('true_false', 'True or False'),
        ('ordering', 'Put in Order'),
        ('writing', 'Free Writing'),
        ('speaking', 'Speaking Practice'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=200)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    instructions = models.TextField()
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
    
    def __str__(self):
        return f"{self.title} ({self.get_exercise_type_display()})"


class Question(models.Model):
    """Questão de um exercício"""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    hint = models.CharField(max_length=200, blank=True)
    explanation = models.TextField(blank=True, help_text="Explicação da resposta correta")
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    """Resposta de uma questão (para múltipla escolha)"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.answer_text} ({'Correct' if self.is_correct else 'Incorrect'})"


class FillBlankAnswer(models.Model):
    """Resposta para exercícios de preencher lacunas"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='fill_blank_answer')
    correct_answer = models.CharField(max_length=200)
    alternative_answers = models.TextField(
        blank=True, 
        help_text="Respostas alternativas aceitas, separadas por vírgula"
    )
    case_sensitive = models.BooleanField(default=False)
    
    def __str__(self):
        return self.correct_answer


class DialogueContent(models.Model):
    """Conteúdo de diálogo (para speaking)"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='dialogues')
    title = models.CharField(max_length=200)
    context = models.TextField(blank=True, help_text="Contexto do diálogo")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class DialogueLine(models.Model):
    """Linha de diálogo"""
    dialogue = models.ForeignKey(DialogueContent, on_delete=models.CASCADE, related_name='lines')
    speaker = models.CharField(max_length=50)
    text = models.TextField()
    translation = models.TextField(blank=True)
    audio = models.FileField(upload_to='audio/dialogues/', blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.speaker}: {self.text[:30]}"


class ExampleBox(models.Model):
    """Caixa de exemplos (aqueles boxes amarelos)"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='example_boxes')
    title = models.CharField(max_length=200, default="Examples")
    content = models.TextField()
    box_type = models.CharField(
        max_length=20,
        choices=[
            ('example', 'Example'),
            ('tip', 'Tip'),
            ('warning', 'Warning'),
            ('info', 'Information'),
        ],
        default='example'
    )
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


# ============= TRACKING DE PROGRESSO DO ALUNO =============

class StudentProgress(models.Model):
    """Progresso do aluno em uma unidade"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    completion_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'unit']
        verbose_name = 'Student Progress'
        verbose_name_plural = 'Student Progress'
    
    def __str__(self):
        return f"{self.student.username} - {self.unit.title} ({self.completion_percentage}%)"


class ExerciseSubmission(models.Model):
    """Submissão de exercício pelo aluno"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    time_spent = models.IntegerField(help_text="Tempo gasto em segundos", null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.exercise.title} ({self.score}/{self.max_score})"


class QuestionResponse(models.Model):
    """Resposta do aluno a uma questão específica"""
    submission = models.ForeignKey(ExerciseSubmission, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField()
    points_earned = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Response to {self.question.id}"