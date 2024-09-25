from rest_framework.decorators import api_view
from .models import Campaign , SendMensagem
from django.http import JsonResponse
from django.core import serializers

@api_view(['GET'])
def list_campaign(request):
    try:
        # Filtra as campanhas que estão ativas (ou de acordo com o status)
        campaigns = serializers.serialize('json', Campaign.objects.all())
        return JsonResponse({ 'campaigns': campaigns }, status=200)
    except Exception as e:
        return JsonResponse({ 'error': str(e) }, status=500)

@api_view(['GET'])
def campaign_details(request, campaign_id):
    try:
        # Filtra as campanhas que estão ativas (ou de acordo com o status)
        campaign = serializers.serialize('json', Campaign.objects.filter(id=campaign_id))
        logs = serializers.serialize('json', SendMensagem.objects.filter(campaign=campaign_id))
        return JsonResponse({ 'campaign': campaign, 'logs': logs }, status=200)
    except Exception as e:
        return JsonResponse({ 'error': str(e) }, status=500)

