from rest_framework import serializers
from .models import Note, SitePinger


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['hash', 'note_type']


class SitePingerSerializer(serializers.ModelSerializer):
    #note = NoteSerializer(many=False, read_only=True)
    note = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source='note.note_type',
        default=None
    )

    class Meta:
        model = SitePinger
        fields = '__all__'
