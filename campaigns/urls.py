from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from .views import (
    CampaignViewSet,
    CampaignCharacterViewSet,
    CampaignInviteViewSet,
    CampaignLogViewSet,
)

router = DefaultRouter()
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"characters",CampaignCharacterViewSet, basename="campaigncharacter")
router.register(r"invites", CampaignInviteViewSet, basename="campaigninvite")
router.register(r"campaign-logs", CampaignLogViewSet, basename="campaign-log")

urlpatterns = [
    path("", include(router.urls)),
]