from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter()
router.register(r"campaigns", views.CampaignViewSet, basename="campaign")
router.register(r"characters", views.CampaignCharacterViewSet, basename="campaigncharacter")
router.register(r"invites", views.CampaignInviteViewSet, basename="campaigninvite")

urlpatterns = [
    path("", include(router.urls)),
]