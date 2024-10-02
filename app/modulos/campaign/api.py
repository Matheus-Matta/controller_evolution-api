from rest_framework.decorators import api_view
from .models import Campaign , SendMensagem, CampaignResponse
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from celery.result import AsyncResult
from app.modulos.instance.models import Instance
from celery_progress.backend import Progress
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.core.serializers import serialize

@api_view(['GET'])
def list_campaign(request):
    try:
        # Obtém os parâmetros de data da query string
        data_inicio = request.GET.get('dataInicio')
        data_fim = request.GET.get('dataFim')

        # Filtrar as campanhas com base no intervalo de datas e ordenar por id decrescente
        campaigns = Campaign.objects.all().order_by('-id')

        # Se dataInicio for passada, filtrar campanhas com start_date >= data_inicio
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            campaigns = campaigns.filter(start_date__gte=data_inicio_obj)

        # Se dataFim for passada, filtrar campanhas com start_date <= data_fim
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            campaigns = campaigns.filter(start_date__lte=data_fim_obj)

        # Serializar os dados e incluir a contagem de respostas para cada campanha
        campaigns_data = []
        for campaign in campaigns:
            response_count = CampaignResponse.objects.filter(campaign=campaign).count()
            campaigns_data.append({
                'id': campaign.id,
                'name': campaign.name,
                'total_numbers': campaign.total_numbers,
                'status': campaign.status,
                'send_success': campaign.send_success,
                'send_error': campaign.send_error,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'response_count': response_count
            })

        return JsonResponse({'campaigns': campaigns_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['GET'])
def campaign_details(request, campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        logs = SendMensagem.objects.filter(campaign=campaign_id)
        responses = CampaignResponse.objects.filter(campaign=campaign).count()
        return JsonResponse({
            'campaign': serializers.serialize('json', [campaign]),  # Serialize a campanha
            'logs': serializers.serialize('json', logs),  # Serialize os logs
            'responses': responses,  # Adicionar contagem de respostas
        }, status=200)
    except Campaign.DoesNotExist:
        return JsonResponse({'error': 'Campanha não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def campaign_encerrar(request, campaign_id):
    if request.method == "POST":
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                if campaign.status != 'finalizado':
                    campaign.end_date = timezone.now()
                    campaign.status = 'cancelado'
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

@api_view(['POST'])
def campaign_add_response(request, instance_name):
    try:
        instance = Instance.objects.get(name=instance_name)
        campaign = Campaign.objects.get(instance=instance)
        number = request.POST.get('number')

        if campaign.status == "processando":
            # Verificar se o número já respondeu
            if not campaign.responses.filter(phone_number=number).exists():
                # Criar uma nova resposta para a campanha
                CampaignResponse.objects.create(
                    campaign=campaign,
                    phone_number=number
                )
                campaign.save()
            else:
                return JsonResponse({"error": "Número já respondeu a esta campanha."}, status=400)
        else:
            return JsonResponse({"error": "Campanha não está processando."}, status=400)

        return JsonResponse({"success": "Resposta registrada para todas as campanhas ativas."}, status=201)

    except Instance.DoesNotExist:
        return JsonResponse({"error": "Instância não encontrada"}, status=404)
    except Campaign.DoesNotExist:
        return JsonResponse({"error": "Campanha não encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Erro ao registrar resposta: {str(e)}"}, status=500)

@api_view(['POST'])
def campaign_delete(request, campaign_id):
    if request.method == "POST":
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                task_id = campaign.id_progress
                              
                result = AsyncResult(task_id)
                result.revoke(terminate=True)

                campaign.delete()

                return JsonResponse({"success": "Campanha deleta com sucesso."}, status=201)
            
            except Campaign.DoesNotExist:
                    return JsonResponse({"error": "Campanha não encontrada"}, status=401)

            except Exception as e:
                    return JsonResponse({"error": f"error ao encerrar campanha {str(e)}"}, status=500)

@api_view(['GET'])
def api_campaign_progress(request, task_id):
    if request.method == "GET":
        try:
            # Obtém o resultado da task do Celery pelo ID da tarefa
            result = AsyncResult(task_id)

            # Verifica o progresso da tarefa
            progress = Progress(result)
            progress_data = progress.get_info()  # Obtém dados como estado e porcentagem

            # Retorna a resposta JSON com o progresso da tarefa
            print(progress_data)
            return JsonResponse({
                'state': progress_data['state'],
                'progress': {
                    'current': progress_data['progress']['current'],
                    'total': progress_data['progress']['total'],
                    'percent': progress_data['progress']['percent'],
                }
            }, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)            