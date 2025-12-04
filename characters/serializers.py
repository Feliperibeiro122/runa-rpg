from rest_framework import serializers
from .models import (
    CharacterBase,
    Origin, OriginLineage,
    Class, Subclass,
    Feature, FeatureOption
)

# BASE CHARACTER

class CharacterBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterBase
        fields = ["id", "name", "biography", "avatar", "created_at"]



# ORIGINS


class OriginLineageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginLineage
        fields = ["id", "name", "description"]


class OriginSerializer(serializers.ModelSerializer):
    lineages = OriginLineageSerializer(many=True, read_only=True)

    class Meta:
        model = Origin
        fields = ["id", "name", "description", "lineages"]



# CLASSES & SUBCLASSES


class SubclassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subclass
        fields = ["id", "name", "description"]


class ClassSerializer(serializers.ModelSerializer):
    subclasses = SubclassSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ["id", "name", "description", "subclasses"]



# FEATURES


class FeatureOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureOption
        fields = ["id", "name", "description"]


class FeatureSerializer(serializers.ModelSerializer):
    options = FeatureOptionSerializer(many=True, read_only=True)

    related = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = [
            "id", "name", "description", "type",
            "level_required", "options", "related"
        ]

    def get_related(self, obj):
        if obj.type == Feature.CLASS:
            return {"class": obj.base_class.name}
        if obj.type == Feature.SUBCLASS:
            return {"subclass": obj.subclass.name}
        return None
