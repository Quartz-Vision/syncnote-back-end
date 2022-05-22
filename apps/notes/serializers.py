from django.db import transaction
from django.http import request
from rest_framework import serializers

from apps.notes.models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ('user',)


class TagListField(serializers.ListField):
    """Need this field to return just plain list of strings"""
    child = serializers.CharField()

    def to_representation(self, data):
        return [item.text for item in data.all()]


class NoteSerializer(serializers.ModelSerializer):
    local_id = serializers.CharField(required=False)  # need it to receive notes' updates

    tags = TagListField(
        allow_empty=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Note
        exclude = ('user',)
        extra_kwargs = {
            'data_size': {'read_only': True}
        }

    def set_tags(self, instance, tags):
        if tags is not None:
            instance.tags.set([
                Tag.objects.get_or_create(user=instance.user, text=text)[0]
                for text in tags
            ])

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        data_size = len(validated_data.get('content'))
        user = getattr(self.context.get('request'), 'user')

        validated_data.pop('local_id', None)

        with transaction.atomic():
            instance = Note.objects.create(
                user=user,
                data_size=data_size,
                **validated_data
            )
            self.set_tags(instance, tags)

        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        content = validated_data.get('content')
        data_size = len(content or '')
        user = getattr(self.context.get('request'), 'user')

        validated_data.pop('local_id', None)
        
        with transaction.atomic():
            instance = super(NoteSerializer, self).update(
                instance,
                validated_data | (
                    {'data_size': data_size} if content is not None else {}
                )
            )
            self.set_tags(instance, tags)

        return instance


class ActionSerializer(serializers.Serializer):
    note_id = serializers.CharField()
    time = serializers.DateTimeField()

    
class ExchangeActionsSerializer(serializers.Serializer):
    last_update_time = serializers.DateTimeField(required=True)
    updates = ActionSerializer(many=True)
    deletions = ActionSerializer(many=True)


class ExchangeActionsResponseSerializer(serializers.Serializer):
    pass


class NotesUpdateResponseSerializer(serializers.Serializer):
    notes_updated = NoteSerializer(many=True)
    notes_to_send = serializers.ListField(child=serializers.CharField())


class NotesUploadResponseSerializer(serializers.Serializer):
    local_id = serializers.CharField()
    remote_id = serializers.CharField()
