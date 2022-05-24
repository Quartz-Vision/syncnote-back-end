from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.notes.models import *
from apps.notes.serializers import *
from apps.notes.services import *


class NotesSyncronisationTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.user = User.objects.create(username='test_user')
        self.days = 20
        self.now = timezone.now()
        self.before_now = self.now - timedelta(minutes=1)

        # we have 20 days with one note each
        Note.objects.bulk_create([
            Note(
                user=self.user,
                title=f'test_note_{i}',
                content=f'test_content_{i}',
                color='#ff0000',
                updated_at=self.now + timedelta(days=i),
            )
            for i in range(self.days)
        ])

    def test_exchange_actions(self):
        # let's update 6 notes, create 2 notes and delete 5 notes (-5 notes)
        updates = [
            {
                'note_id': str(note_id),
                'time': self.now + timedelta(days=self.days+1)
            }
            for note_id in self.user.notes.all().values_list('id', flat=True)[:6]
        ]
        updates += [
            {
                'note_id': f'new_note_{i}',
                'time': self.now + timedelta(days=self.days+i)
            }
            for i in range(2)
        ]
        deletions = [
            {
                'note_id': str(note_id),
                'time': self.now + timedelta(days=self.days+1)
            }
            for note_id in self.user.notes.all().values_list('id', flat=True)[6:11]
        ]
        # then try to delete the same notes again (-0 notes)
        deletions += [
            {
                'note_id': str(note_id),
                'time': self.now + timedelta(days=self.days+1)
            }
            for note_id in self.user.notes.all().values_list('id', flat=True)[6:11]
        ]
        # and try to delete but with much earlier time (-0 notes)
        deletions += [
            {
                'note_id': str(note_id),
                'time': self.now - timedelta(days=self.days)
            }
            for note_id in self.user.notes.all().values_list('id', flat=True)[11:20]
        ]

        result = exchange_actions(
            user=self.user,
            updates=updates,
            deletions=deletions,
            last_update_time=self.now + timedelta(days=self.days+1)
        )

        self.assertEqual(
            self.user.notes.all().count(),
            self.days - 5,
        )
        self.assertCountEqual(
            result['update_requested'],
            [action['note_id'] for action in updates],
        )

        # wihout last update time
        result = exchange_actions(
            user=self.user,
            updates=[],
            deletions=[]
        )

        self.assertEqual(
            self.user.notes.all().count(),
            len(result['update_on_client'])
        )
        self.assertEqual(
            self.user.deletions.all().count(),
            len(result['deletions'])
        )

    def tearDown(self):
        self.user.delete()
