from rest_framework import serializers
from .models import Campaign, CampaignCharacter, CampaignInvite, CharacterSkill, CampaignLog
from characters.serializers import (
    CharacterBaseSerializer,
    OriginSerializer, OriginLineageSerializer,
    ClassSerializer, SubclassSerializer,
    FeatureSerializer, FeatureOptionSerializer
)
# SKILLS
class CharacterSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    ability = serializers.CharField(source="skill.ability", read_only=True)
    total = serializers.IntegerField(source="total_value", read_only=True)  # calculado na model

    class Meta:
        model = CharacterSkill
        fields = [
            "id",
            "skill",  # id da skill base
            "skill_name",
            "ability",
            "proficiency_level",
            "total",
        ]

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
    available_actions = serializers.SerializerMethodField()
    base_character = CharacterBaseSerializer(read_only=True)

    origin = OriginSerializer(read_only=True)
    lineage = OriginLineageSerializer(read_only=True)
    char_class = ClassSerializer(read_only=True)
    subclass = SubclassSerializer(read_only=True)

    chosen_features = FeatureSerializer(many=True, read_only=True)
    chosen_feature_options = FeatureOptionSerializer(many=True, read_only=True)

    skills = CharacterSkillSerializer(many=True, read_only=True)

    user_name = serializers.CharField(source="user.username", read_only=True)

    status = serializers.CharField(read_only=True)

    def get_available_actions(self, obj):
        request = self.context.get("request")
        if not request:
            return []

        return obj.available_actions(request.user)

    class Meta:
        model = CampaignCharacter
        fields = [
            "id", "campaign", "base_character", "user", "user_name",
            "name", "level",
            "status",
            "available_actions",
            "origin", "lineage",
            "char_class", "subclass",
            "chosen_features", "chosen_feature_options",
            "skills",
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

class CharacterSkillUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSkill
        fields = ["proficiency_level"]

    def validate_proficiency_level(self, value):
        if value not in [0, 1, 2]:
            raise serializers.ValidationError(
                "Nível de proficiência inválido."
            )
        return value
    
class CampaignLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source="actor.username",
        read_only=True
    )

    class Meta:
        model = CampaignLog
        fields = [
            "id",
            "type",
            "message",
            "actor",
            "actor_name",
            "created_at"
        ]