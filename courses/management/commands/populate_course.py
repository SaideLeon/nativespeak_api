from django.core.management.base import BaseCommand
from courses.models import Unit, Theme, Topic, VocabularyItem, GrammarContent, GrammarExample, Exercise, Question, FillBlankAnswer, DialogueContent, DialogueLine, ExampleBox

class Command(BaseCommand):
    help = 'Popula o banco com Unit 3: Daily Life'

    def handle(self, *args, **kwargs):
        # Criar Unit
        unit = Unit.objects.create(
            number=3,
            title="Daily Life",
            description="Learn to talk about your everyday routines and activities",
            icon="📚",
            order=3,
            is_active=True
        )
        
        # Theme 1: Food and Eating Habits
        theme1 = Theme.objects.create(
            unit=unit,
            title="Food and Eating Habits",
            icon="🍽️",
            order=1,
            is_active=True
        )
        
        # Topic: Vocabulary
        vocab_topic = Topic.objects.create(
            theme=theme1,
            title="Types of Food",
            topic_type="vocabulary",
            icon="📝",
            order=1,
            is_active=True
        )
        
        # Vocabulary Items
        vocab_items = [
            ("Breakfast", "Café da manhã", "brek-fəst", "I usually have breakfast at 7 AM."),
            ("Lunch", "Almoço", "lʌntʃ", "We eat lunch together every day."),
            ("Dinner", "Jantar", "dɪn-ər", "What time do you have dinner?"),
            ("Snack", "Lanche", "snæk", "I need a snack between meals."),
            ("Meal", "Refeição", "miːl", "This is my favorite meal of the day."),
            ("Beverage", "Bebida", "bev-ər-ɪdʒ", "What beverage would you like?"),
        ]
        
        for i, (word, translation, pronunciation, example) in enumerate(vocab_items, 1):
            VocabularyItem.objects.create(
                topic=vocab_topic,
                word=word,
                translation=translation,
                pronunciation=pronunciation,
                example_sentence=example,
                order=i
            )
        
        # Example Box para Vocabulary
        ExampleBox.objects.create(
            topic=vocab_topic,
            title="💡 Examples",
            content="• I usually have breakfast at 7 AM.\n• We eat lunch together every day.\n• What time do you have dinner?",
            box_type="example",
            order=1
        )
        
        # Topic: Grammar
        grammar_topic = Topic.objects.create(
            theme=theme1,
            title="Present Simple (Daily Routines)",
            topic_type="grammar",
            icon="📖",
            description="We use Present Simple to talk about habits and routines.",
            order=2,
            is_active=True
        )
        
        # Grammar Content
        grammar_content = GrammarContent.objects.create(
            topic=grammar_topic,
            title="Present Simple Rules",
            explanation="We use Present Simple to talk about habits and routines. Add -s/-es for he/she/it.",
            order=1
        )
        
        # Grammar Examples
        grammar_examples = [
            ("I / You / We / They", "eat", "I eat breakfast at 8 AM."),
            ("He / She / It", "eats", "She eats lunch at noon."),
            ("I / You / We / They", "drink", "They drink coffee every morning."),
            ("He / She / It", "drinks", "He drinks tea in the afternoon."),
        ]
        
        for i, (subject, verb, example) in enumerate(grammar_examples, 1):
            GrammarExample.objects.create(
                grammar_content=grammar_content,
                subject=subject,
                verb_form=verb,
                example_sentence=example,
                order=i
            )
        
        # Exercise: Fill in the Blanks
        exercise = Exercise.objects.create(
            topic=grammar_topic,
            title="Complete the sentences",
            exercise_type="fill_blank",
            instructions="Fill in the blanks with the correct form of the verb in parentheses.",
            order=1,
            points=30
        )
        
        # Questions
        questions_data = [
            ("I _______ (eat) breakfast every morning.", "eat", "Use the base form for I/You/We/They", "We use 'eat' without -s for I/You/We/They"),
            ("My brother _______ (drink) coffee in the morning.", "drinks", "Add -s for he/she/it", "We add -s to the verb for he/she/it: drinks"),
            ("We _______ (have) dinner at 7 PM.", "have", "Use the base form for I/You/We/They", "We use 'have' without -s for We"),
        ]
        
        for i, (question_text, answer, hint, explanation) in enumerate(questions_data, 1):
            question = Question.objects.create(
                exercise=exercise,
                question_text=question_text,
                hint=hint,
                explanation=explanation,
                order=i,
                points=10
            )
            
            FillBlankAnswer.objects.create(
                question=question,
                correct_answer=answer,
                case_sensitive=False
            )
        
        # Topic: Speaking
        speaking_topic = Topic.objects.create(
            theme=theme1,
            title="Talking About Meals",
            topic_type="speaking",
            icon="💬",
            order=3,
            is_active=True
        )
        
        # Dialogue
        dialogue = DialogueContent.objects.create(
            topic=speaking_topic,
            title="🗣️ Dialogue Model",
            context="Two friends talking about their eating habits",
            order=1
        )
        
        # Dialogue Lines
        dialogue_lines = [
            ("A", "What do you usually have for breakfast?", "O que você costuma comer no café da manhã?"),
            ("B", "I usually have cereal and orange juice. What about you?", "Eu geralmente como cereal e suco de laranja. E você?"),
            ("A", "I prefer toast with jam and coffee.", "Eu prefiro torrada com geleia e café."),
            ("B", "That sounds delicious!", "Isso parece delicioso!"),
        ]
        
        for i, (speaker, text, translation) in enumerate(dialogue_lines, 1):
            DialogueLine.objects.create(
                dialogue=dialogue,
                speaker=speaker,
                text=text,
                translation=translation,
                order=i
            )
        
        # Theme 2: Daily Routines
        theme2 = Theme.objects.create(
            unit=unit,
            title="Daily Routines",
            icon="⏰",
            order=2,
            is_active=True
        )
        
        # Topic: Daily Activities Vocabulary
        daily_vocab_topic = Topic.objects.create(
            theme=theme2,
            title="Daily Activities",
            topic_type="vocabulary",
            icon="📝",
            order=1,
            is_active=True
        )
        
        # Daily Activities Vocabulary
        daily_vocab = [
            ("Wake up", "Acordar", "I wake up at 6:30 AM."),
            ("Get dressed", "Vestir-se", "I get dressed after breakfast."),
            ("Go to work", "Ir ao trabalho", "I go to work at 8 AM."),
            ("Come back", "Voltar", "I come back home at 6 PM."),
            ("Take a shower", "Tomar banho", "I take a shower in the evening."),
            ("Go to bed", "Ir dormir", "I go to bed at 11 PM."),
        ]
        
        for i, (word, translation, example) in enumerate(daily_vocab, 1):
            VocabularyItem.objects.create(
                topic=daily_vocab_topic,
                word=word,
                translation=translation,
                example_sentence=example,
                order=i
            )
        
        # Example Box
        ExampleBox.objects.create(
            topic=daily_vocab_topic,
            title="💡 My Daily Routine",
            content="• I wake up at 6:30 AM.\n• I take a shower and get dressed.\n• I go to work at 8 AM.\n• I come back home at 6 PM.\n• I go to bed at 11 PM.",
            box_type="example",
            order=1
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Unit 3: Daily Life criada com sucesso!'))