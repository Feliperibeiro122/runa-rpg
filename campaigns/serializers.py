from rest_framework import serializers
from .models import Campaign, CampaignCharacter, CampaignInvite
from characters.serializers import (
    CharacterBaseSerializer,
    OriginSerializer, OriginLineageSerializer,
    ClassSerializer, SubclassSerializer,
    FeatureSerializer, FeatureOptionSerializer
)


# CAMPAIGN


class CampaignSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    players_count = serializers.IntegerField(source="players.count", read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id", "name", "description",
            "owner", "owner_name",
            "players", "players_count",
            "created_at",
        ]



# CAMPAIGN CHARACTER (FICHA)


class CampaignCharacterSerializer(serializers.ModelSerializer):
    base_character = CharacterBaseSerializer(read_only=True)

    origin = OriginSerializer(read_only=True)
    lineage = OriginLineageSerializer(read_only=True)
    char_class = ClassSerializer(read_only=True)
    subclass = SubclassSerializer(read_only=True)

    chosen_features = FeatureSerializer(many=True, read_only=True)
    chosen_feature_options = FeatureOptionSerializer(many=True, read_only=True)

    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = CampaignCharacter
        fields = [
            "id", "campaign", "base_character", "user", "user_name",
            "name", "level",
            "origin", "lineage",
            "char_class", "subclass",
            "chosen_features", "chosen_feature_options",
            "strength", "dexterity", "constitution",
            "intelligence", "wisdom", "charisma",
            "hp", "mana", "sanity",
            "notes",
        ]



# CAMPAIGN INVITE

class CampaignInviteSerializer(serializers.ModelSerializer):
    invited_user_name = serializers.CharField(source="invited_user.username", read_only=True)
    invited_by_name = serializers.CharField(source="invited_by.username", read_only=True)

    class Meta:
        model = CampaignInvite
        fields = [
            "id", "campaign",
            "invited_user", "invited_user_name",
            "invited_by", "invited_by_name",
            "status", "created_at", "responded_at"
        ]
