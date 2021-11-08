from typing import Iterable
from uuid import UUID
from django.db.models import QuerySet, Q

from apps.notes.serializers import NoteSerializer

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


def update_notes(notes: QuerySet, updated_notes: list[dict], context: dict) -> list[dict]:
    serializer = NoteSerializer(context=context)
    local_remote_ids = []

    for updated in updated_notes:
        local_id = updated['local_id']
        try:
            note = notes.filter(id=UUID(local_id)).first()
        except ValueError:
            note = None

        if note:
            serializer.update(note, updated)
        else:
            db_id = str(serializer.create(updated).id)
            local_remote_ids.append({
                'local_id': local_id,
                'remote_id': db_id
            })

    return local_remote_ids
