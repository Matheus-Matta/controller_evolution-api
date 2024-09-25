from rest_framework.decorators import api_view
from .models import Campaign , SendMensagem
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from celery.result import AsyncResult

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


@api_view(['POST'])
def campaign_encerrar(request, campaign_id):
    if request.method == "POST":
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                if campaign.status != 'finalizado':
                    campaign.end_date = timezone.now()
                    campaign.status = 'finalizado'
                    campaign.save()
                    task_id = campaign.id_progress
                              
                    # Cancela a task no Celery
                    result = AsyncResult(task_id)
                    result.revoke(terminate=True)
                    return JsonResponse({"success": "Campanha encerrada com sucesso."}, status=201)
                else:
                   return JsonResponse({"error": "Campanha ja encerrada."}, status= 200)
            except Campaign.DoesNotExist:
                    return JsonResponse({"error": "Campanha não encontrada"}, status=401)

            except Exception as e:
                    return JsonResponse({"error": f"error ao encerrar campanha {str(e)}"}, status=500)

    
