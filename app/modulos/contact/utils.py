from django.core.exceptions import ValidationError
from .models import Contact
from app.modulos.tags.models import Tag
import openpyxl
import xlrd
import re
import chardet
from django.core.paginator import Paginator

def create_contact(instance, user, name, number, tags):
    if Contact.objects.filter(user=user, number=number).exists():
        return None
    if instance and user and name and number:
        contact = Contact.objects.create(
                        instance=instance,
                        user=user,
                        name=name,
                        number=number
                    )
        for tag_name in tags:
            add_tag_to_contact(contact, tag_name, user)
        return contact
    return False


def get_contacts(request):
    # Obtém a consulta de pesquisa e a tag da URL
    tag_name = request.GET.get('tag')
    contact_name = request.GET.get('name')
    contacts = Contact.objects.filter(user=request.user)
    
    # Filtra por tag, se fornecido
    if tag_name:
        tag = Tag.objects.filter(user=request.user, name__icontains=tag_name).first()
        if tag:
            contacts = contacts.filter(tags=tag)
    # Filtra por nome, se fornecido
    if contact_name:
        contacts = contacts.filter(name__icontains=contact_name)

    # Configuração da paginação
    paginator = Paginator(contacts, 100)  # Mostra 100 contatos por página
    page_number = request.GET.get('page')  # Obtém o número da página da URL
    page_obj = paginator.get_page(page_number) # Obtém os contatos da página atual

    # Total de contatos
    total_contacts = contacts.count()
    # Obtém as tags do usuário
    tags = Tag.objects.filter(user=request.user).distinct()
        
    context = { 
            'contacts': page_obj.object_list,  # Contatos da página atual
            'page_obj': page_obj,              # Objeto da página para controle no template
            'tags': tags,                      # Tags do usuário
            'total_contacts': total_contacts,  # Quantidade total de contatos
            'tag_name': tag_name if tag_name else False,
            'name': contact_name if contact_name else False,
            'filter': True if tag_name or contact_name else False
    }
    return context


def add_tag_to_contact(contact, tag_name, user):
    tag, created = Tag.objects.get_or_create(name=tag_name, user=user)
    contact.tags.add(tag)

def detect_encoding(file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.workbook = None
        self.sheet = None

        if file_path.endswith('.xls'):
            self.load_xls()
        elif file_path.endswith('.xlsx'):
            self.load_xlsx()
        else:
            raise ValueError("formato insuportado, formato do arquivo deve ser .xls ou .xlsx")
        
    def load_xls(self):
        detected_encoding = detect_encoding(self.file_path)
        self.workbook = xlrd.open_workbook(self.file_path, encoding_override=detected_encoding)
        self.sheet = self.workbook.sheet_by_index(0)  # Assume que estamos trabalhando com a primeira aba

    def load_xlsx(self):
        self.workbook = openpyxl.load_workbook(self.file_path)
        self.sheet = self.workbook.active  # Assume que estamos trabalhando com a primeira aba

    def column_letter_to_index(self, letter):
        # Converte letra da coluna em índice (A=0, B=1, ..., Z=25, AA=26, etc.)
        index = 0
        for i, char in enumerate(reversed(letter)):
            index += (ord(char.upper()) - ord('A') + 1) * (26 ** i)
        return index - 1
    
   
    def validate_phone_number(self, phone_number):
        try:
            # Converte o número para string
            phone_number = str(phone_number)
            # Verifica se o número está vazio após a conversão
            if not phone_number:
                return False
            # Remove todos os caracteres não numéricos
            phone_number = re.sub(r'\D', '', phone_number)
            # Verifica se o número já contém o código do país (55)
            if not phone_number.startswith('55'):
                # Adiciona o código do país (55) se não estiver presente e o número tiver 10 ou 11 dígitos
                if len(phone_number) == 10 or len(phone_number) == 11:
                    phone_number = f'55{phone_number}'
                else:
                    return False  # Número inválido se não tiver o tamanho esperado

            # Valida o formato 5521912345678
            if re.match(r'^55\d{10,12}$', phone_number):
                return phone_number
            else:
                return False  # Número inválido
        except Exception as e:
            print(f'[ERROR] >> Numero invalido: {str(e)}')
            return False
      
    def get_contacts(self, number_column, name_column, limit=None):
        try:
            contacts = []
            if self.file_path.endswith('.xls'):
                final = self.sheet.nrows
                if limit:
                    final = min(limit + 1, final)
                number_index = self.column_letter_to_index(number_column)
                name_index = self.column_letter_to_index(name_column)
                for i in range(1, final):
                    numero_celular = self.sheet.cell_value(i, number_index)
                    nome = self.sheet.cell_value(i, name_index)
                    numero_celular = self.validate_phone_number(numero_celular)
                    if not numero_celular or not nome:
                        continue
                    contacts.append({
                        'name': nome,
                        'number': numero_celular,
                    })
            elif self.file_path.endswith('.xlsx'):
                final = self.sheet.max_row
                if limit:
                    final = min(limit + 1, final)
                for i in range(2, final + 1):  # Começa em 2 para pular o cabeçalho
                    numero_celular = self.sheet[f'{number_column}{i}'].value
                    nome = self.sheet[f'{name_column}{i}'].value
                    numero_celular = self.validate_phone_number(numero_celular)
                    if not numero_celular or not nome:
                        continue
                    contacts.append({
                        'name': nome,
                        'number': numero_celular,
                    })
        except Exception as e:
            print(f'[ERROR] >> extrair excel: {str(e)}')
            return False
        
        return contacts
        