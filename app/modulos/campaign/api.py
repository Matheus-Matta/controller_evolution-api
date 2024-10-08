from rest_framework.decorators import api_view
from .models import Campaign , SendMensagem, CampaignMessage
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
            response_count = CampaignMessage.objects.filter(campaigns=campaign, status='respondida').count()
            campaigns_data.append({
                'id': campaign.id,
                'name': campaign.name,
                'total_numbers': campaign.total_numbers,
                'status': campaign.status,
                'send_success': campaign.send_success,
                'send_error': campaign.send_error,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'response_count': response_count,
                'id_progress': campaign.id_progress,
            })

        return JsonResponse({'campaigns': campaigns_data}, status=200)

    except Exception as e:
        print(f"error {e}")
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['GET'])
def campaign_details(request, campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        logs = SendMensagem.objects.filter(campaign=campaign_id)
        responses = CampaignMessage.objects.filter(campaigns=campaign)

        # Serializar a campanha
        campaign_data = {
            'id': campaign.id,
            'name': campaign.name,
            'total_numbers': campaign.total_numbers,
            'status': campaign.status,
            'send_success': campaign.send_success,
            'send_error': campaign.send_error,
            'start_date': campaign.start_date,
            'end_date': campaign.end_date,
            'id_progress': campaign.id_progress,
        }

        # Serializar os logs
        logs_data = serializers.serialize('json', logs)

        # Serializar as respostas
        responses_data = []
        for response in responses:
            responses_data.append({
                'numero': response.numero,
                'status': response.status,
                'response_date': response.response_date,
                'response_message': response.response_message,
            })

        return JsonResponse({
            'campaign': campaign_data,
            'logs': logs_data,
            'responses': responses_data,
        }, status=200)
    except Campaign.DoesNotExist:
        return JsonResponse({'error': 'Campanha não encontrada'}, status=404)
    except Exception as e:
        print(f"error {e}")
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
                    print(f"error {e}")
                    return JsonResponse({"error": f"error ao encerrar campanha {str(e)}"}, status=500)

@api_view(['POST'])
def campaign_add_response(request, instance_name):
    try:
        # Obtém a instância pelo nome
        instance = Instance.objects.get(name=instance_name)

        # Obtém o número e o conteúdo da mensagem do request
        number = request.data.get('number')
        message_content = request.data.get('message')

        if not number:
            return JsonResponse({"error": "Número não encontrado"}, status=400)

        # Encontra todas as CampaignMessage pendentes para este número e instância
        pending_messages = CampaignMessage.objects.filter(
            numero=number,
            instance=instance,
            status='pendente'
        )

        if not pending_messages.exists():
            return JsonResponse({"error": "Nenhuma campanha aguardando resposta para este número."}, status=400)

        for campaign_message in pending_messages:
            # Atualiza o status para 'respondida' e registra a data e a mensagem de resposta
            campaign_message.status = 'respondida'
            campaign_message.response_date = timezone.now()
            campaign_message.response_message = message_content
            campaign_message.save()

            # Incrementa o contador de respostas nas campanhas associadas
            for campaign in campaign_message.campaigns.all():
                if campaign.status != "cancelado":
                    # Incrementa o contador de respostas
                    SendMensagem.objects.create(
                        campaign=campaign,
                        numero=number,
                        status='response',
                        code=200,
                        msg=message_content
                    )
                    campaign.response_count += 1
                    campaign.save()

                else:
                    continue  # Ignora campanhas canceladas

            # Opcional: Adiciona a resposta ao log (pode ser implementado conforme sua necessidade)

        print('Resposta registrada para as campanhas ativas.', instance_name, number)
        return JsonResponse({"success": "Resposta registrada com sucesso."}, status=201)

    except Instance.DoesNotExist:
        return JsonResponse({"error": "Instância não encontrada"}, status=400)
    except Exception as e:
        print(f"error {e}")
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
                    print(f"error {e}")
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