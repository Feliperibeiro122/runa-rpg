from django.contrib import admin
from .models import (
    CharacterBase,
    Origin, OriginLineage,
    Class, Subclass,
    Feature, FeatureOption
)


# CHARACTER BASE

@admin.register(CharacterBase)
class CharacterBaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)



# ORIGINS & LINEAGES


class OriginLineageInline(admin.TabularInline):
    model = OriginLineage
    extra = 1


@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [OriginLineageInline]


@admin.register(OriginLineage)
class OriginLineageAdmin(admin.ModelAdmin):
    list_display = ("id", "origin", "name")
    list_filter = ("origin",)
    search_fields = ("name", "origin__name")


# CLASSES & SUBCLASSES

class SubclassInline(admin.TabularInline):
    model = Subclass
    extra = 1


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [SubclassInline]


@admin.register(Subclass)
class SubclassAdmin(admin.ModelAdmin):
    list_display = ("id", "base_class", "name")
    list_filter = ("base_class",)
    search_fields = ("name", "base_class__name")



# FEATURES & OPTIONS


class FeatureOptionInline(admin.TabularInline):
    model = FeatureOption
    extra = 1


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "level_required", "related_to")
    list_filter = ("type", "level_required", "base_class", "subclass")
    search_fields = ("name", "description")
    inlines = [FeatureOptionInline]

    def related_to(self, obj):
        if obj.type == Feature.CLASS:
            return f"Classe: {obj.base_class}"
        if obj.type == Feature.SUBCLASS:
            return f"Subclasse: {obj.subclass}"
        return "-"
    related_to.short_description = "Vinculado a"


@admin.register(FeatureOption)
class FeatureOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "feature", "name")
    search_fields = ("name", "feature__name")

