from ast import List
from typing import Any
from django.forms import ModelForm, FileField, FileInput, CharField, Textarea, ValidationError
from term_project.scheduler.models import DataSet
from django.core.validators import FileExtensionValidator
import csv
import io
import jsonschema


class DatasetCreationForm(ModelForm):

    description = CharField(
        widget=Textarea(attrs={'rows': 3})
    )
    dataset_file = FileField(
        required=True, 
        allow_empty_file=False,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=FileInput(attrs={'accept': '.csv'})
    )
    class Meta:
        model = DataSet
        fields = ['title', 'description', 'dataset_file']

    def clean_dataset_file(self) -> dict[str, list[Any]]:
        """Clean csv file."""
        csv_file = io.TextIOWrapper(
            self.cleaned_data['dataset_file'], 
        )
        reader = csv.DictReader(csv_file)

        cource_schema = {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'required': ['cource_code', 'population'],
                'properties': {
                    'cource_code': {'type': 'string'},
                    'population': {'type': 'number'},
                },
            },
        }

        venue_schema = {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'required': ['venue_code', 'examination_capacity'],
                'properties': {
                    'venue_code': {'type': 'string'},
                    'examination_capacity': {'type': 'number'},
                },
            },
        }

        cource_content = []
        venue_content = []

        for row in reader:
            try:
                if row.get('cource_code') and row.get('cource_code'):
                    cource_content.append(
                        {
                            'cource_code': row['cource_code'].replace(' ', ''),
                            'population': int(row['population'])
                        }
                    )
                
                if row.get('venue_code') and row.get('examination_capacity'):
                    venue_content.append(
                        {
                            'venue_code': row['venue_code'].replace(' ', ''),
                            'examination_capacity': int(row['examination_capacity']),
                        }
                    )
            except ValueError as error:
                raise ValidationError('Invalid datatype') from error

        try:
            jsonschema.validate(instance=cource_content, schema=cource_schema)
            jsonschema.validate(instance=venue_content, schema=venue_schema)
        except jsonschema.ValidationError as error:
            raise ValidationError(error.message)

        return {
            'cources': cource_content,
            'venues': venue_content,
        }

