from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class CharacterBase(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=120)
    biography = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='characters/avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
    
# ===========================================================
# ORIGENS & LINHAGENS
# ===========================================================

class Origin(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class OriginLineage(models.Model):
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE, related_name="lineages")
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.origin.name} - {self.name}"


# ===========================================================
# CLASSES & SUBCLASSES
# ===========================================================

class Class(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Subclass(models.Model):
    base_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subclasses")
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return f"{self.base_class.name} - {self.name}"


# ===========================================================
# FEATURES & FEATURES OPTIONS
# ===========================================================

class Feature(models.Model):
    CLASS = "class"
    SUBCLASS = "subclass"

    FEATURE_TYPE_CHOICES = [
        (CLASS, "Classe"),
        (SUBCLASS, "Subclasse"),
    ]

    type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES)

    # Se for feature de classe, usa esse
    base_class = models.ForeignKey(Class, null=True, blank=True,
                                   on_delete=models.CASCADE, related_name="features")

    # Se for de subclasse, usa esse
    subclass = models.ForeignKey(Subclass, null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="features")

    name = models.CharField(max_length=150)
    description = models.TextField()
    level_required = models.IntegerField(default=1)

    def clean(self):
        from django.core.exceptions import ValidationError

        # Feature de classe precisa de classe
        if self.type == self.CLASS and not self.base_class:
            raise ValidationError("Features de classe precisam estar ligadas a uma Classe.")

        # Feature de subclasse precisa de subclasse
        if self.type == self.SUBCLASS and not self.subclass:
            raise ValidationError("Features de subclasse precisam estar ligadas a uma Subclasse.")

        # Não pode ter ambos
        if self.base_class and self.subclass:
            raise ValidationError("Uma Feature não pode ter Classe e Subclasse ao mesmo tempo.")

    def __str__(self):
        return self.name


class FeatureOption(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return f"{self.feature.name} - {self.name}"