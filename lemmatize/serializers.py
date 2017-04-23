from rest_framework import serializers

from lemmatize.models import Lemma


class LemmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lemma
        fields = ('name', 'meets_count')