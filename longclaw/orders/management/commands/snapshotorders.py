from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Saves snapshot data of each OrderItem from it\'s related ProductVariant'

