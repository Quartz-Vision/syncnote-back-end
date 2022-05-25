from datetime import datetime
from functools import reduce
import operator
from typing import Optional

from django.db.models import F, Max, OuterRef, Q, Subquery
from django.contrib.auth import get_user_model
from apps.common.services import filter_valid_uuids

from apps.notes.models import Deletion, Note
from apps.notes.serializers import ActionSerializer, NoteSerializer
from apps.notes.types import ActionDict, ClientServerIdsDict


User = get_user_model()


def exchange_actions(
    user: User,
    updates: list[ActionDict],
    deletions: list[ActionDict],
    last_update_time: Optional[datetime] = None,
) -> dict:
    """
    Returns updates and sync list in the format of ExchangeActionsResponseSerializer
    """

    # sync deletions

    # need this to use fk in queries
    valid_deletion_ids = filter_valid_uuids([action['note_id'] for action in deletions])
    valid_deletion_ids_set = set(valid_deletion_ids)

    existing_deleted_notes_ids = set(
        str(id)
        for id in Note.objects.filter(
            user=user,
            id__in=valid_deletion_ids
        ).values_list('id', flat=True)
    ) if deletions else set()
    
    Deletion.objects.bulk_create([
        Deletion(
            user=user,
            note_static_id=action['note_id'],
            # so that fk will be created only for already existing notes
            note_id=action['note_id'] if action['note_id'] in existing_deleted_notes_ids else None,
            deleted_at=action['time']
        )
        for action in deletions
        if action['note_id'] in valid_deletion_ids_set
    ])

    user.notes.annotate(
        last_deletion_time=Max('deletions__deleted_at')
    ).filter(
        updated_at__lt=F('last_deletion_time')
    ).delete()

    # optimize deletions
    user.deletions.exclude(
        id=Subquery(
            user.deletions
            .filter(note_static_id=OuterRef('note_static_id'))
            .order_by('-deleted_at')
            .values('id')[:1]
        )
    ).delete()

    db_new_deletions = (
        user.deletions.filter(created_at__gt=last_update_time) if last_update_time
        else user.deletions.all()
    )
    new_deletions = ActionSerializer(
        data=[
            {
                'note_id': note_id,
                'time': time
            }
            for note_id, time in db_new_deletions.values_list('note_static_id', 'deleted_at')
        ],
        many=True
    )
    new_deletions.is_valid()
    new_deletions = new_deletions.data
 
    # gether updates and requests

    client_updated_notes_ids = set(action['note_id'] for action in updates)
    valid_updated_notes_ids = set(filter_valid_uuids(client_updated_notes_ids))
    valid_updates = [action for action in updates if action['note_id'] in valid_updated_notes_ids]
    
    create_requested_ids = client_updated_notes_ids - valid_updated_notes_ids
    update_requested_ids = set(
        user.notes
        .annotate(last_deletion_time=Max('deletions__deleted_at'))
        .filter(
            reduce(
                operator.or_, 
                [Q(id=action['note_id'], updated_at__lte=action['time']) for action in valid_updates]
            )
            & (
                Q(updated_at__lt=F('last_deletion_time'))
                | Q(last_deletion_time__isnull=True)
            )
        )
        .distinct()
        .values_list('id', flat=True)
    ) if valid_updates else set()
    
    server_updated_notes = (
        user.notes.filter(Q(created_at__gt=last_update_time) | Q(updated_at__gt=last_update_time))
            if last_update_time
        else user.notes.all()
    )  

    return {
        'update_on_client': [
            NoteSerializer(instance=note).data
            for note in server_updated_notes
        ],
        'update_requested': [str(id) for id in create_requested_ids | update_requested_ids],
        'deletions': new_deletions
    }


def apply_updates(user: User, updated_notes: list[dict], context: dict = None) -> list[ClientServerIdsDict]:
    valid_updated_notes_ids = set(filter_valid_uuids(
        [note['server_id'] for note in updated_notes]
    ))

    serializer = NoteSerializer(context=context)
    client_server_ids: list[ClientServerIdsDict] = []

    for note in updated_notes:
        if note['server_id'] in valid_updated_notes_ids and user.notes.filter(id=note['server_id']).exists():
            serializer.update(user.notes.get(id=note['server_id']), note)
        else:
            client_id = note['server_id']
            db_id = str(serializer.create(note).id)  # it will change note dict
            
            client_server_ids.append({
                'client_note_id': str(client_id),
                'server_note_id': db_id
            })

    return client_server_ids
