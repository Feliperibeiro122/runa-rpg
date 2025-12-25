from django.db import models
from django.conf import settings
from characters.models import (
    CharacterBase,
    Origin, OriginLineage,
    Class, Subclass,
    Feature, FeatureOption,
)
from django.core.exceptions import ValidationError

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

    def log(self, *, actor, message):
        CampaignLog.objects.create(
            campaign=self,
            actor=actor,
            message=message
        )

    def __str__(self):
        return self.name

class CampaignCharacter(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        ACTIVE = "active", "Ativo"
        DEAD = "dead", "Morto"
        RETIRED = "retired", "Aposentado"
        REMOVED = "removed", "Removido"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    def can_change_status(self, new_status, user):
        if new_status == self.status:
            return False, "O personagem já está nesse status."
        
        # não pode mudar se já foi removido
        if self.status == self.Status.REMOVED:
            return (
                user == self.campaign.owner,
                "Apenas o mestre pode alterar um personagem removido."
            )

        # regras por status atual
        if self.status == self.Status.DRAFT:
            if new_status == self.Status.ACTIVE:
                return self.user == user, "Apenas o dono pode ativar o personagem."

        if self.status == self.Status.ACTIVE:
            if new_status in [self.Status.DEAD, self.Status.REMOVED]:
                return self.campaign.owner == user, "Apenas o mestre pode fazer isso."
            if new_status == self.Status.RETIRED:
                return self.user == user, "Apenas o dono pode aposentar o personagem."
            
        # DEAD → ACTIVE (reviver / inimigo / NPC)
        if self.status == self.Status.DEAD:
            if new_status == self.Status.ACTIVE:
                return self.campaign.owner == user, "Apenas o mestre pode reativar."

    # RETIRED → ACTIVE (voltar à campanha)
        if self.status == self.Status.RETIRED:
            if new_status == self.Status.ACTIVE:
                return self.campaign.owner == user, "Apenas o mestre pode reativar."

        return False, "Transição de status inválida."
    
    def change_status(self, new_status, user):
        allowed, message = self.can_change_status(new_status, user)
        if not allowed:
            raise ValidationError(message)

        old_status = self.status
        self.status = new_status
        self.save()

        self.campaign.log(
            actor=user,
            message=f"{self.name}: {old_status} → {new_status}"
        )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="characters")
    base_character = models.ForeignKey(CharacterBase, on_delete=models.SET_NULL, null=True, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Informações da ficha para ESSA campanha
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=1)

    # Escolhas definitivas do player
    origin = models.ForeignKey(Origin, on_delete=models.SET_NULL, null=True)
    lineage = models.ForeignKey(OriginLineage, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.lineage and self.lineage.origin != self.origin:
            raise ValidationError("A linhagem não pertence à origem escolhida.")

    char_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    subclass = models.ForeignKey(Subclass, on_delete=models.SET_NULL, null=True, blank=True)

    # Features e opções
    chosen_features = models.ManyToManyField(Feature, blank=True)
    chosen_feature_options = models.ManyToManyField(FeatureOption, blank=True)

    # Atributos dessa campanha
    strength = models.IntegerField(default=8)
    dexterity = models.IntegerField(default=8)
    constitution = models.IntegerField(default=8)
    intelligence = models.IntegerField(default=8)
    wisdom = models.IntegerField(default=8)
    charisma = models.IntegerField(default=8)

    # Recursos variáveis da campanha
    hp = models.IntegerField(default=0)
    mana = models.IntegerField(default=0)
    sanity = models.IntegerField(default=60)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (Lv {self.level}) em {self.campaign.name}"

# --- MODIFICADORES ---
    @property
    def strength_mod(self): return (self.strength - 10) // 2
    @property
    def dexterity_mod(self): return (self.dexterity - 10) // 2
    @property
    def constitution_mod(self): return (self.constitution - 10) // 2
    @property
    def intelligence_mod(self): return (self.intelligence - 10) // 2
    @property
    def wisdom_mod(self): return (self.wisdom - 10) // 2
    @property
    def charisma_mod(self): return (self.charisma - 10) // 2

    # --- PROFICIÊNCIA ---
    @property
    def proficiency_bonus(self):
        return 2 + ((self.level - 1) // 4)

    def __str__(self):
        return f"{self.name} - {self.campaign.name}"
    
class Skill(models.Model):
    ABILITY_CHOICES = [
        ("strength", "Força"),
        ("dexterity", "Destreza"),
        ("constitution", "Constituição"),
        ("intelligence", "Inteligência"),
        ("wisdom", "Sabedoria"),
        ("charisma", "Carisma"),
    ]

    name = models.CharField(max_length=100)
    ability = models.CharField(max_length=20, choices=ABILITY_CHOICES)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class CharacterSkill(models.Model):
    character = models.ForeignKey(
        CampaignCharacter,
        on_delete=models.CASCADE,
        related_name="skills"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    # 0 = nada, 1 = proficiente, 2 = expertise
    proficiency_level = models.IntegerField(default=0)

    class Meta:
        unique_together = ("character", "skill")

    def __str__(self):
        return f"{self.character} - {self.skill}"

    def clean(self):
        if self.proficiency_level not in [0, 1, 2]:
            raise ValidationError("Nível de proficiência inválido.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_value(self):
        ability_mod = getattr(self.character, f"{self.skill.ability}_mod")
        prof = self.character.proficiency_bonus

        if self.proficiency_level == 1:
            return ability_mod + prof
        if self.proficiency_level == 2:
            return ability_mod + (prof * 2)

        return ability_mod

    
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

class CampaignLog(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.campaign.name}] {self.message}"
