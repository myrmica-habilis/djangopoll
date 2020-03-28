import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse('demo:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        past_question = create_question(question_text='Past question.', days=-30)
        response = self.client.get(reverse('demo:index'))
        question_list = response.context['latest_question_list']
        self.assertEqual(len(question_list), 1)
        self.assertEqual(question_list[0], past_question)

    def test_future_question(self):
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('demo:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        past_question = create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('demo:index'))
        question_list = response.context['latest_question_list']
        self.assertEqual(len(question_list), 1)
        self.assertEqual(question_list[0], past_question)

    def test_two_past_questions(self):
        past_question_1 = create_question(question_text='Past question 1.', days=-30)
        past_question_2 = create_question(question_text='Past question 2.', days=-5)
        response = self.client.get(reverse('demo:index'))
        question_list = response.context['latest_question_list']
        self.assertEqual(len(question_list), 2)
        self.assertEqual(question_list[0], past_question_1)
        self.assertEqual(question_list[1], past_question_2)


class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('demo:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past question.', days=-5)
        url = reverse('demo:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertFalse(future_question.was_published_recently())

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)

        self.assertFalse(old_question.was_published_recently())

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)

        self.assertTrue(recent_question.was_published_recently())
