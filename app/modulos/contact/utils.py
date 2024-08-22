from django.core.exceptions import ValidationError
from .models import Contact
from app.modulos.tags.models import Tag
import openpyxl
import xlrd
import re
import chardet

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
        phone_number = re.sub(r'\D', '', phone_number)  # Remove todos os caracteres não numéricos

        # Verifica se o número já contém o código do país (55)
        if not phone_number.startswith('55'):
            # Adiciona o código do país (55) se não estiver presente e o número tiver 10 ou 11 dígitos
            if len(phone_number) == 10 or len(phone_number) == 11:  # Considerando DDD + número
                phone_number = f'55{phone_number}'
            else:
                return False  # Número inválido se não tiver o tamanho esperado

        # Valida o formato 5521912345678
        if re.match(r'^55\d{10,12}$', phone_number):
            return phone_number
        else:
            return False  # Número inválido
    
    def get_contacts(self, number_column, name_column, limit=None):
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
        return contacts