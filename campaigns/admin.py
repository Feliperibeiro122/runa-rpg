from django.contrib import admin
from .models import Campaign, CampaignCharacter, CampaignInvite, Skill, CharacterSkill


# ===========================================================
# INLINE: CampaignCharacter dentro de Campaign
# ===========================================================

class CampaignCharacterInline(admin.TabularInline):
    model = CampaignCharacter
    extra = 0
    readonly_fields = ("user", "level", "char_class", "subclass")
    fields = ("name", "user", "level", "char_class", "subclass")
    show_change_link = True


# ===========================================================
# INLINE: CampaignInvite dentro de Campaign
# ===========================================================

class CampaignInviteInline(admin.TabularInline):
    model = CampaignInvite
    extra = 0
    readonly_fields = ("invited_user", "status", "created_at", "responded_at")
    fields = ("invited_user", "status", "created_at", "responded_at")
    show_change_link = True


# ===========================================================
# ADMIN: Campaign
# ===========================================================

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at", "player_count")
    search_fields = ("name", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    inlines = [CampaignCharacterInline, CampaignInviteInline]

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Nº de Jogadores"


# Inline para CharacterSkill

class CharacterSkillInline(admin.TabularInline):
    model = CharacterSkill
    extra = 0
    readonly_fields = ("total_value",)

# ===========================================================
# ADMIN: CampaignCharacter
# ===========================================================

@admin.register(CampaignCharacter)
class CampaignCharacterAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "campaign", "user",
        "level", "char_class", "subclass",
    )
    search_fields = ("name", "user__username", "campaign__name")
    list_filter = ("campaign", "char_class", "subclass", "level")
    ordering = ("campaign", "name")
    
    inlines = [CharacterSkillInline]

    fieldsets = (
        ("Informações Gerais", {
            "fields": ("campaign", "base_character", "user", "name", "level")
        }),
        ("Origem", {
            "fields": ("origin", "lineage")
        }),
        ("Classe e Subclasse", {
            "fields": ("char_class", "subclass")
        }),
        ("Atributos", {
            "fields": (
                "strength", "dexterity", "constitution",
                "intelligence", "wisdom", "charisma",
            )
        }),
        ("Recursos", {
            "fields": ("hp", "mana", "sanity")
        }),
        ("Escolhas de Features", {
            "fields": ("chosen_features", "chosen_feature_options")
        }),
        ("Anotações", {
            "fields": ("notes",)
        }),
    )

# Skill Admin

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "ability")
    search_fields = ("name",)
    list_filter = ("ability",)


# CharacterSkill Admin

@admin.register(CharacterSkill)
class CharacterSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "character", "skill", "proficiency_level", "total_value")
    list_filter = ("skill", "proficiency_level")
    search_fields = ("character__name", "skill__name")

# ===========================================================
# ADMIN: CampaignInvite
# ===========================================================

@admin.register(CampaignInvite)
class CampaignInviteAdmin(admin.ModelAdmin):
    list_display = (
        "id", "campaign", "invited_user", "invited_by",
        "status", "created_at", "responded_at"
    )
    search_fields = ("campaign__name", "invited_user__username")
    list_filter = ("status", "campaign", "created_at")
    ordering = ("-created_at",)

