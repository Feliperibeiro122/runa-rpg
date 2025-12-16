from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Campaign, CampaignCharacter, CampaignInvite, CharacterSkill
from .serializers import (
    CampaignSerializer,
    CampaignCharacterSerializer,
    CampaignInviteSerializer,
    CharacterSkillSerializer,
    CharacterSkillUpdateSerializer
)
from .permissions import IsCampaignOwner,IsCharacterOwner,IsInviteReceiver, IsCampaignOwnerForCharacter, IsCampaignCharacterPlayer, CanEditCharacterResources

def campaigns(request):
    return render(request, "campaigns/campaigns.html")

class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Campaign.objects.filter(
            Q(owner=user) | Q(players=user)
        ).distinct()
    
    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCampaignOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # owner da campanha é sempre o usuário logado
        serializer.save(owner=self.request.user)

    # ----------------------------------------
    # LISTAR PERSONAGENS DA CAMPANHA
    # ----------------------------------------
    @action(detail=True, methods=["get"])
    def characters(self, request, pk=None):
        campaign = self.get_object()
        chars = CampaignCharacter.objects.filter(campaign=campaign)
        serializer = CampaignCharacterSerializer(chars, many=True)
        return Response(serializer.data)

    # ----------------------------------------
    # LISTAR CONVITES
    # ----------------------------------------
    @action(detail=True, methods=["get"])
    def invites(self, request, pk=None):
        campaign = self.get_object()
        invites = CampaignInvite.objects.filter(campaign=campaign)
        serializer = CampaignInviteSerializer(invites, many=True)
        return Response(serializer.data)

    # ----------------------------------------
    # ENVIAR CONVITE
    # ----------------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsCampaignOwner])
    def invite(self, request, pk=None):
        campaign = self.get_object()
        invited_user_id = request.data.get("user_id")

        if not invited_user_id:
            return Response({"error": "user_id é obrigatório"}, status=400)

        invite = CampaignInvite.objects.create(
            campaign=campaign,
            invited_user_id=invited_user_id,
            invited_by=request.user
        )

        return Response(CampaignInviteSerializer(invite).data, status=201)

class CampaignCharacterViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignCharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = CampaignCharacter.objects.filter(
            Q(user=user) |
            Q(campaign__owner=user) |
            Q(campaign__players=user)
        ).distinct()

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


    
    def get_permissions(self):
    # leitura (GET, LIST, retrieve)
        if self.action in ["retrieve", "list", "skills"]:
            return [IsAuthenticated(), IsCampaignCharacterPlayer()]

    # editar ficha
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), CanEditCharacterResources()]

    # deletar personagem
        if self.action == "destroy":
            return [IsAuthenticated(), IsCampaignOwnerForCharacter()]

        return [IsAuthenticated()]

    # ----------------------------------------
    # ATUALIZAR UMA SKILL EXATA
    # ----------------------------------------
    @action(detail=True, methods=["patch"])
    def update_skill(self, request, pk=None):
        character = self.get_object()

        skill_id = request.data.get("skill")
        level = request.data.get("proficiency_level")

        if skill_id is None or level is None:
            return Response({"error": "Informe skill e proficiency_level"}, status=400)

        try:
            char_skill = CharacterSkill.objects.get(character=character, skill_id=skill_id)
        except CharacterSkill.DoesNotExist:
            return Response({"error": "Skill não encontrada para este personagem."}, status=404)

        serializer = CharacterSkillUpdateSerializer(
            char_skill,
            data={"proficiency_level": level},
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            CharacterSkillSerializer(char_skill).data
        )



    # ----------------------------------------
    # LISTAR AS SKILLS DO PERSONAGEM
    # ----------------------------------------
    @action(detail=True, methods=["get"])
    def skills(self, request, pk=None):
        character = self.get_object()
        serializer = CharacterSkillSerializer(character.skills.all(), many=True)
        return Response(serializer.data)
    
    #STATUS DO PERSONAGEM
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        character = self.get_object()

        try:
            character.change_status(
                CampaignCharacter.Status.ACTIVE,
                request.user
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=403)

        return Response({"status": "Personagem ativado."})
    
    @action(detail=True, methods=["post"])
    def kill(self, request, pk=None):
        character = self.get_object()

        try:
            character.change_status(
                CampaignCharacter.Status.DEAD,
                request.user
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=403)

        return Response({"status": "Personagem morto."})


    @action(detail=True, methods=["post"])
    def retire(self, request, pk=None): 
        character = self.get_object() 
        try:
            character.change_status( CampaignCharacter.Status.RETIRED, request.user )
        except ValidationError as e:
            return Response({"error": e.message}, status=403) 
        
        return Response({"status": "Personagem aposentado."})

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None): 
        character = self.get_object() 
        try:
            character.change_status( CampaignCharacter.Status.REMOVED, request.user )
        except ValidationError as e:
            return Response({"error": e.message}, status=403) 
        
        return Response({"status": "Personagem removido da campanha."})


class CampaignInviteViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignInviteSerializer
    permission_classes = [IsAuthenticated,IsInviteReceiver]

    def get_queryset(self):
        return CampaignInvite.objects.filter(
        invited_user=self.request.user
        )

    # aceitar convite
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        invite = self.get_object()

        if invite.status != "pending":
            return Response(
        {"error": "Este convite já foi respondido."},
        status=400
        )

        invite.status = "accepted"
        invite.responded_at = timezone.now()
        invite.save()

        invite.campaign.players.add(request.user)

        return Response({"status": "Convite aceito."})

    # recusar convite
    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        invite = self.get_object()

        if invite.status != "pending":
            return Response(
        {"error": "Este convite já foi respondido."},
        status=400
        )

        invite.status = "rejected"
        invite.responded_at = timezone.now()
        invite.save()

        return Response({"status": "Convite recusado."})


