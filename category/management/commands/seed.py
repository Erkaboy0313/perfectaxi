from django.core.management.base import BaseCommand
from django.db import transaction


def set_translations(obj, translations: dict):
    """Set parler translations for a model instance.
    translations: {'en': {'field': 'value', ...}, 'ru': {...}, 'uz': {...}}
    """
    for lang, fields in translations.items():
        obj.set_current_language(lang)
        for field, value in fields.items():
            setattr(obj, field, value)
        obj.save()


class Command(BaseCommand):
    help = 'Seed the database with default reference data required to run the project.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing reference data before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self._seed_car_services()
        self._seed_car_brends()
        self._seed_colors()
        self._seed_reject_reasons()
        self._seed_services()
        self._seed_search_radius()

        self.stdout.write(self.style.SUCCESS('Default data seeded successfully.'))

    # ------------------------------------------------------------------
    # Reset helpers
    # ------------------------------------------------------------------

    def _reset(self):
        from category.models import CarService, CarBrend, CarModel, Color
        from order.models import RejectReason, Services
        from ws.models import SearchRadius

        CarModel.objects.all().delete()
        CarBrend.objects.all().delete()
        CarService.objects.all().delete()
        Color.objects.all().delete()
        RejectReason.objects.all().delete()
        Services.objects.all().delete()
        SearchRadius.objects.all().delete()
        self.stdout.write('Existing reference data deleted.')

    # ------------------------------------------------------------------
    # CarService  (TranslatableModel)
    # ------------------------------------------------------------------

    def _seed_car_services(self):
        from category.models import CarService

        services_data = [
            {
                'service': CarService.ServiceChoices.STANDART,
                'start_price': 5000,
                'price_per_km': 800.0,
                'price_per_min': 100.0,
                'wait_price_per_min': 150.0,
                'free_wait_time': 3,
                'translations': {
                    'en': {'includedCars': 'Chevrolet Nexia, Cobalt, Lacetti'},
                    'ru': {'includedCars': 'Chevrolet Nexia, Cobalt, Lacetti'},
                    'uz': {'includedCars': 'Chevrolet Nexia, Cobalt, Lacetti'},
                },
            },
            {
                'service': CarService.ServiceChoices.COMFORT,
                'start_price': 8000,
                'price_per_km': 1200.0,
                'price_per_min': 150.0,
                'wait_price_per_min': 200.0,
                'free_wait_time': 3,
                'translations': {
                    'en': {'includedCars': 'Chevrolet Malibu, Spark, Onix'},
                    'ru': {'includedCars': 'Chevrolet Malibu, Spark, Onix'},
                    'uz': {'includedCars': 'Chevrolet Malibu, Spark, Onix'},
                },
            },
            {
                'service': CarService.ServiceChoices.BUSSINESS,
                'start_price': 15000,
                'price_per_km': 2000.0,
                'price_per_min': 250.0,
                'wait_price_per_min': 300.0,
                'free_wait_time': 5,
                'translations': {
                    'en': {'includedCars': 'Hyundai Sonata, Kia K5, Mercedes'},
                    'ru': {'includedCars': 'Hyundai Sonata, Kia K5, Mercedes'},
                    'uz': {'includedCars': 'Hyundai Sonata, Kia K5, Mercedes'},
                },
            },
        ]

        for data in services_data:
            translations = data.pop('translations')
            obj, created = CarService.objects.get_or_create(
                service=data['service'],
                defaults=data,
            )
            set_translations(obj, translations)
            self._log('CarService', obj.service, created)

    # ------------------------------------------------------------------
    # CarBrend + CarModel  (both TranslatableModel)
    # ------------------------------------------------------------------

    def _seed_car_brends(self):
        from category.models import CarBrend, CarModel

        brends_data = [
            {
                'translations': {'en': {'name': 'Chevrolet'}, 'ru': {'name': 'Chevrolet'}, 'uz': {'name': 'Chevrolet'}},
                'models': [
                    {'en': 'Nexia', 'ru': 'Nexia', 'uz': 'Nexia'},
                    {'en': 'Cobalt', 'ru': 'Cobalt', 'uz': 'Cobalt'},
                    {'en': 'Lacetti', 'ru': 'Lacetti', 'uz': 'Lacetti'},
                    {'en': 'Malibu', 'ru': 'Malibu', 'uz': 'Malibu'},
                    {'en': 'Spark', 'ru': 'Spark', 'uz': 'Spark'},
                    {'en': 'Onix', 'ru': 'Onix', 'uz': 'Onix'},
                    {'en': 'Damas', 'ru': 'Дамас', 'uz': 'Damas'},
                ],
            },
            {
                'translations': {'en': {'name': 'Hyundai'}, 'ru': {'name': 'Хюндай'}, 'uz': {'name': 'Hyundai'}},
                'models': [
                    {'en': 'Sonata', 'ru': 'Соната', 'uz': 'Sonata'},
                    {'en': 'Elantra', 'ru': 'Элантра', 'uz': 'Elantra'},
                    {'en': 'Tucson', 'ru': 'Туссан', 'uz': 'Tucson'},
                    {'en': 'Santa Fe', 'ru': 'Санта Фе', 'uz': 'Santa Fe'},
                ],
            },
            {
                'translations': {'en': {'name': 'Kia'}, 'ru': {'name': 'Киа'}, 'uz': {'name': 'Kia'}},
                'models': [
                    {'en': 'K5', 'ru': 'K5', 'uz': 'K5'},
                    {'en': 'Rio', 'ru': 'Рио', 'uz': 'Rio'},
                    {'en': 'Sportage', 'ru': 'Спортейдж', 'uz': 'Sportage'},
                ],
            },
            {
                'translations': {'en': {'name': 'Toyota'}, 'ru': {'name': 'Тойота'}, 'uz': {'name': 'Toyota'}},
                'models': [
                    {'en': 'Camry', 'ru': 'Камри', 'uz': 'Camry'},
                    {'en': 'Corolla', 'ru': 'Королла', 'uz': 'Corolla'},
                    {'en': 'Land Cruiser', 'ru': 'Ленд Крузер', 'uz': 'Land Cruiser'},
                ],
            },
            {
                'translations': {'en': {'name': 'Nexia'}, 'ru': {'name': 'Нексия'}, 'uz': {'name': 'Nexia'}},
                'models': [
                    {'en': 'N1', 'ru': 'N1', 'uz': 'N1'},
                    {'en': 'N3', 'ru': 'N3', 'uz': 'N3'},
                ],
            },
            {
                'translations': {'en': {'name': 'Mercedes-Benz'}, 'ru': {'name': 'Мерседес'}, 'uz': {'name': 'Mercedes-Benz'}},
                'models': [
                    {'en': 'E-Class', 'ru': 'Е-класс', 'uz': 'E-Class'},
                    {'en': 'S-Class', 'ru': 'С-класс', 'uz': 'S-Class'},
                ],
            },
        ]

        for brend_data in brends_data:
            models_data = brend_data.pop('models')
            translations = brend_data.pop('translations')

            # Use English name as a stable lookup key
            en_name = translations['en']['name']

            # Find existing brend by English translation
            existing = None
            for b in CarBrend.objects.language('en').all():
                if b.name == en_name:
                    existing = b
                    break

            if existing:
                brend_obj = existing
                created = False
            else:
                brend_obj = CarBrend()
                brend_obj.save()
                created = True

            set_translations(brend_obj, translations)
            self._log('CarBrend', en_name, created)

            # Car models under this brand
            for model_names in models_data:
                en_model_name = model_names['en']

                existing_model = None
                for m in CarModel.objects.language('en').filter(brend=brend_obj):
                    if m.name == en_model_name:
                        existing_model = m
                        break

                if existing_model:
                    model_obj = existing_model
                    model_created = False
                else:
                    model_obj = CarModel(brend=brend_obj)
                    model_obj.save()
                    model_created = True

                set_translations(model_obj, {
                    'en': {'name': model_names['en']},
                    'ru': {'name': model_names['ru']},
                    'uz': {'name': model_names['uz']},
                })
                self._log('  CarModel', en_model_name, model_created)

    # ------------------------------------------------------------------
    # Color  (TranslatableModel)
    # ------------------------------------------------------------------

    def _seed_colors(self):
        from category.models import Color

        colors_data = [
            {'en': 'White',  'ru': 'Белый',    'uz': 'Oq'},
            {'en': 'Black',  'ru': 'Чёрный',   'uz': 'Qora'},
            {'en': 'Silver', 'ru': 'Серебристый', 'uz': 'Kumush'},
            {'en': 'Grey',   'ru': 'Серый',    'uz': 'Kulrang'},
            {'en': 'Red',    'ru': 'Красный',  'uz': 'Qizil'},
            {'en': 'Blue',   'ru': 'Синий',    'uz': 'Ko\'k'},
            {'en': 'Green',  'ru': 'Зелёный',  'uz': 'Yashil'},
            {'en': 'Yellow', 'ru': 'Жёлтый',  'uz': 'Sariq'},
            {'en': 'Brown',  'ru': 'Коричневый', 'uz': 'Jigarrang'},
            {'en': 'Orange', 'ru': 'Оранжевый', 'uz': 'To\'q sariq'},
        ]

        for color_names in colors_data:
            en_name = color_names['en']

            existing = None
            for c in Color.objects.language('en').all():
                if c.name == en_name:
                    existing = c
                    break

            if existing:
                obj = existing
                created = False
            else:
                obj = Color()
                obj.save()
                created = True

            set_translations(obj, {
                'en': {'name': color_names['en']},
                'ru': {'name': color_names['ru']},
                'uz': {'name': color_names['uz']},
            })
            self._log('Color', en_name, created)

    # ------------------------------------------------------------------
    # RejectReason
    # ------------------------------------------------------------------

    def _seed_reject_reasons(self):
        from order.models import RejectReason

        reasons = [
            'Passenger not found',
            'Passenger cancelled',
            'Wrong address',
            'Too far from pickup',
            'No luggage space',
            'Personal reasons',
        ]

        for name in reasons:
            _, created = RejectReason.objects.get_or_create(name=name)
            self._log('RejectReason', name, created)

    # ------------------------------------------------------------------
    # Services (additional ride services)
    # ------------------------------------------------------------------

    def _seed_services(self):
        from order.models import Services

        services = [
            {'name': 'Baby seat',      'cost': 5000},
            {'name': 'Pet transport',  'cost': 10000},
            {'name': 'Extra luggage',  'cost': 8000},
        ]

        for data in services:
            _, created = Services.objects.get_or_create(
                name=data['name'],
                defaults={'cost': data['cost']},
            )
            self._log('Services', data['name'], created)

    # ------------------------------------------------------------------
    # SearchRadius
    # ------------------------------------------------------------------

    def _seed_search_radius(self):
        from ws.models import SearchRadius

        if not SearchRadius.objects.exists():
            SearchRadius.objects.create(
                radius1=1000,
                radius2=2000,
                radius3=3000,
                radius4=5000,
            )
            self._log('SearchRadius', 'default', True)
        else:
            self._log('SearchRadius', 'default', False)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _log(self, model, name, created):
        if created:
            self.stdout.write(f'  [+] {model}: {name}')
        else:
            self.stdout.write(f'  [=] {model}: {name} (already exists)')
