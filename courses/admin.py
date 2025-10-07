from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Unit, Theme, Topic, VocabularyItem, GrammarContent, GrammarExample,
    Exercise, Question, Answer, FillBlankAnswer, DialogueContent, DialogueLine,
    ExampleBox, StudentProgress, ExerciseSubmission, QuestionResponse
)


# ============= INLINES =============

class ThemeInline(admin.TabularInline):
    model = Theme
    extra = 1
    fields = ['title', 'icon', 'order', 'is_active']


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ['title', 'topic_type', 'icon', 'order', 'is_active']


class VocabularyItemInline(admin.TabularInline):
    model = VocabularyItem
    extra = 3
    fields = ['word', 'translation', 'pronunciation', 'example_sentence', 'order']


class GrammarExampleInline(admin.TabularInline):
    model = GrammarExample
    extra = 2
    fields = ['subject', 'verb_form', 'example_sentence', 'translation', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'hint', 'order', 'points']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['answer_text', 'is_correct', 'order']


class DialogueLineInline(admin.TabularInline):
    model = DialogueLine
    extra = 3
    fields = ['speaker', 'text', 'translation', 'order']


class ExampleBoxInline(admin.StackedInline):
    model = ExampleBox
    extra = 1
    fields = ['title', 'content', 'box_type', 'order']


class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0
    can_delete = False
    readonly_fields = ['question', 'student_answer', 'is_correct', 'points_earned']
    
    def has_add_permission(self, request, obj=None):
        return False


# ============= ADMIN CLASSES =============

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'icon', 'order', 'is_active', 'theme_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order', 'number']
    inlines = [ThemeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'title', 'description', 'icon')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def theme_count(self, obj):
        return obj.themes.count()
    theme_count.short_description = 'Themes'


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'icon', 'order', 'is_active', 'topic_count']
    list_filter = ['unit', 'is_active']
    search_fields = ['title']
    ordering = ['unit', 'order']
    inlines = [TopicInline]
    
    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'theme', 'topic_type', 'icon', 'order', 'is_active', 'content_preview']
    list_filter = ['topic_type', 'is_active', 'theme__unit']
    search_fields = ['title', 'description']
    ordering = ['theme', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('theme', 'title', 'topic_type', 'icon')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    # Inlines dinâmicos baseados no tipo de tópico
    def get_inlines(self, request, obj=None):
        inlines = [ExampleBoxInline]
        
        if obj:
            if obj.topic_type == 'vocabulary':
                inlines.append(VocabularyItemInline)
            elif obj.topic_type == 'speaking':
                # DialogueContent não é inline aqui
                pass
        
        return inlines
    
    def content_preview(self, obj):
        vocab_count = obj.vocabulary_items.count()
        exercise_count = obj.exercises.count()
        dialogue_count = obj.dialogues.count()
        
        parts = []
        if vocab_count:
            parts.append(f"{vocab_count} vocab")
        if exercise_count:
            parts.append(f"{exercise_count} exercises")
        if dialogue_count:
            parts.append(f"{dialogue_count} dialogues")
        
        return ", ".join(parts) if parts else "No content"
    content_preview.short_description = 'Content'


@admin.register(VocabularyItem)
class VocabularyItemAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'topic', 'pronunciation', 'has_audio', 'order']
    list_filter = ['topic__theme__unit', 'topic']
    search_fields = ['word', 'translation', 'example_sentence']
    ordering = ['topic', 'order']
    
    fieldsets = (
        ('Word Information', {
            'fields': ('topic', 'word', 'translation', 'pronunciation')
        }),
        ('Media', {
            'fields': ('image', 'audio')
        }),
        ('Example', {
            'fields': ('example_sentence',)
        }),
        ('Settings', {
            'fields': ('order',)
        }),
    )
    
    def has_audio(self, obj):
        return '✓' if obj.audio else '✗'
    has_audio.short_description = 'Audio'


@admin.register(GrammarContent)
class GrammarContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'example_count', 'order']
    list_filter = ['topic__theme__unit']
    search_fields = ['title', 'explanation']
    ordering = ['topic', 'order']
    inlines = [GrammarExampleInline]
    
    def example_count(self, obj):
        return obj.examples.count()
    example_count.short_description = 'Examples'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'exercise_type', 'question_count', 'points', 'order']
    list_filter = ['exercise_type', 'topic__theme__unit']
    search_fields = ['title', 'instructions']
    ordering = ['topic', 'order']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('topic', 'title', 'exercise_type')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Settings', {
            'fields': ('order', 'points')
        }),
    )
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'exercise', 'points', 'has_hint', 'order']
    list_filter = ['exercise__topic__theme__unit', 'exercise']
    search_fields = ['question_text', 'hint']
    ordering = ['exercise', 'order']
    
    fieldsets = (
        ('Question', {
            'fields': ('exercise', 'question_text', 'hint')
        }),
        ('Answer Information', {
            'fields': ('explanation',)
        }),
        ('Settings', {
            'fields': ('order', 'points')
        }),
    )
    
    def get_inlines(self, request, obj=None):
        if obj and obj.exercise.exercise_type == 'multiple_choice':
            return [AnswerInline]
        return []
    
    def question_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_preview.short_description = 'Question'
    
    def has_hint(self, obj):
        return '✓' if obj.hint else '✗'
    has_hint.short_description = 'Hint'


@admin.register(FillBlankAnswer)
class FillBlankAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'correct_answer', 'case_sensitive', 'has_alternatives']
    list_filter = ['case_sensitive']
    search_fields = ['correct_answer', 'alternative_answers']
    
    def has_alternatives(self, obj):
        return '✓' if obj.alternative_answers else '✗'
    has_alternatives.short_description = 'Has Alternatives'


@admin.register(DialogueContent)
class DialogueContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'line_count', 'order']
    list_filter = ['topic__theme__unit']
    search_fields = ['title', 'context']
    ordering = ['topic', 'order']
    inlines = [DialogueLineInline]
    
    def line_count(self, obj):
        return obj.lines.count()
    line_count.short_description = 'Lines'


@admin.register(ExampleBox)
class ExampleBoxAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'box_type', 'content_preview', 'order']
    list_filter = ['box_type', 'topic__theme__unit']
    search_fields = ['title', 'content']
    ordering = ['topic', 'order']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'


# ============= STUDENT PROGRESS ADMIN =============

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'unit', 'completion_bar', 'started_at', 'completed_at']
    list_filter = ['unit', 'completed_at']
    search_fields = ['student__username', 'unit__title']
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'
    
    def completion_bar(self, obj):
        percentage = obj.completion_percentage
        color = '#28a745' if percentage == 100 else '#007bff' if percentage >= 50 else '#ffc107'
        return format_html(
            '<div style="width:100px; background:#e9ecef; border-radius:5px;">'
            '<div style="width:{}px; background:{}; height:20px; border-radius:5px; text-align:center; color:white; line-height:20px;">'
            '{}%'
            '</div></div>',
            percentage, color, percentage
        )
    completion_bar.short_description = 'Progress'


@admin.register(ExerciseSubmission)
class ExerciseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'exercise', 'score_display', 'submitted_at', 'time_display']
    list_filter = ['exercise__topic__theme__unit', 'submitted_at']
    search_fields = ['student__username', 'exercise__title']
    readonly_fields = ['submitted_at', 'score', 'max_score']
    date_hierarchy = 'submitted_at'
    inlines = [QuestionResponseInline]
    
    def score_display(self, obj):
        percentage = (obj.score / obj.max_score * 100) if obj.max_score > 0 else 0
        color = '#28a745' if percentage >= 70 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}/{} ({}%)</span>',
            color, obj.score, obj.max_score, int(percentage)
        )
    score_display.short_description = 'Score'
    
    def time_display(self, obj):
        if obj.time_spent:
            minutes = obj.time_spent // 60
            seconds = obj.time_spent % 60
            return f"{minutes}m {seconds}s"
        return "-"
    time_display.short_description = 'Time Spent'


# Customização do admin site
admin.site.site_header = "English Course Admin"
admin.site.site_title = "English Course Admin Portal"
admin.site.index_title = "Welcome to English Course Administration"