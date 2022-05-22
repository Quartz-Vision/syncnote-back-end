from datetime import datetime
from typing import Iterable
from uuid import UUID

from django.db.models import QuerySet, Subquery, Case, Sum, Max, F, OuterRef
from django.contrib.auth import get_user_model

from apps.notes.models import Deletion, Note
from apps.notes.serializers import NoteSerializer


User = get_user_model()


def create_or_update_notes():
    pass


def filter_valid_uuids(ids: Iterable) -> set[str]:
    uuids = set()

    for id in ids:
        try:
            uuids.add(str(UUID(id)))
        except ValueError:
            pass
    
    return uuids


def get_notes_update_diff(notes: QuerySet, checklist: list[dict]) -> dict:
    """
    Returns updates and sync list in the format of NotesUpdateResponseSerializer
    """
    checklist_ids = {note['id'] for note in checklist}
    checklist_update_time = {note['id']: note['updated_at'] for note in checklist}

    # need it to filter "ids to send" later
    db_checklist_ids = {str(id) for id in notes.values_list('id', flat=True)}

    notes_updated = []
    notes_to_send = set()

    for note in notes:
        db_id = str(note.id)
        if db_id not in checklist_ids or checklist_update_time[db_id] < note.updated_at:
            notes_updated.append(NoteSerializer(instance=note).data)

        elif checklist_update_time[db_id] > note.updated_at:
            notes_to_send.add(db_id)

    return {
        'notes_updated': notes_updated,
        'notes_to_send': list(notes_to_send | (checklist_ids - db_checklist_ids))
    }


def update_notes(notes: QuerySet, updates: list[dict], context: dict) -> list[dict]:
    serializer = NoteSerializer(context=context)
    local_remote_ids = []

    for update in updates:
        local_id = update['local_id']
        try:
            note = notes.filter(id=UUID(local_id)).first()
        except ValueError:
            note = None

        if note:
            serializer.update(note, update)
        else:
            db_id = str(serializer.create(update).id)
            local_remote_ids.append({
                'local_id': local_id,
                'remote_id': db_id
            })

    return local_remote_ids


def exchange_actions(user: User, updates: list[dict], deletions: list[dict], last_update_time: datetime) -> dict:
    """
    Returns updates and sync list in the format of ExchangeActionsResponseSerializer
    """

    # sync deletions
    Deletion.objects.bulk_create([
        Deletion(
            user=user,
            note_id=deletion['note_id'],
            deleted_at=deletion['time']
        )
        for deletion in deletions
    ])

    user.notes.filter(
        updated_at__lt=Subquery(
            user.deletions
            .filter(note_id=OuterRef('id'))
            .order_by('-deleted_at')
            .values('deleted_at')[:1]
        )
    ).delete()

    # optimize deletions
    user.deletions.exclude(
        id=Subquery(
            user.deletions
            .filter(note_id=OuterRef('note_id'))
            .order_by('-deleted_at')
            .values('id')[:1]
        )
    ).delete()

    # gether updates and requests

    # notes = user.notes.all()
    # notes_updated = update_notes(notes, updates, {'request': None})
    # notes_to_send = filter_valid_uuids(notes_updated)

    # return {
    #     'last_update_time': user.last_update_time,
    #     'updates': [{
    #         'note_id': note_id,
    #         'time': user.last_update_time
    #     } for note_id in notes_to_send],
    #     'deletions': [{
    #         'note_id': note_id,
    #         'time': user.last_update_time
    #     } for note_id in filter_valid_uuids(deletions)]
    # }