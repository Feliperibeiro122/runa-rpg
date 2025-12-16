from rest_framework.permissions import BasePermission


class IsCampaignOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsCampaignPlayer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user or
            request.user in obj.players.all()
        )

class IsCharacterOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsCampaignCharacterPlayer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.campaign.owner == request.user or
            request.user in obj.campaign.players.all()
        )
    
class IsCampaignOwnerForCharacter(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.campaign.owner == request.user    

class CanEditCharacterResources(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            obj.campaign.owner == request.user
        )

class IsInviteReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.invited_user == request.user
