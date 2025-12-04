from django.db import models
from django.conf import settings
from characters.models import (
    CharacterBase,
    Origin, OriginLineage,
    Class, Subclass,
    Feature, FeatureOption,
)

User = settings.AUTH_USER_MODEL


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_campaigns"
    )

    players = models.ManyToManyField(
        User,
        related_name="joined_campaigns",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CampaignCharacter(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="characters")
    base_character = models.ForeignKey(CharacterBase, on_delete=models.CASCADE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Informações da ficha para ESSA campanha
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=1)

    # Escolhas definitivas do player
    origin = models.ForeignKey(Origin, on_delete=models.SET_NULL, null=True)
    lineage = models.ForeignKey(OriginLineage, on_delete=models.SET_NULL, null=True)

    char_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    subclass = models.ForeignKey(Subclass, on_delete=models.SET_NULL, null=True, blank=True)

    # Features e opções
    chosen_features = models.ManyToManyField(Feature, blank=True)
    chosen_feature_options = models.ManyToManyField(FeatureOption, blank=True)

    # Atributos dessa campanha
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    constitution = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    charisma = models.IntegerField(default=10)

    # Recursos variáveis da campanha
    hp = models.IntegerField(default=0)
    mana = models.IntegerField(default=0)
    sanity = models.IntegerField(default=100)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (Lv {self.level}) em {self.campaign.name}"
    
class CampaignInvite(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (PENDING, "Pendente"),
        (ACCEPTED, "Aceito"),
        (REJECTED, "Recusado"),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="invites")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invites")
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invites")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("campaign", "invited_user")  # evita duplicar convites

    def __str__(self):
        return f"Convite para {self.invited_user} na campanha {self.campaign}"
