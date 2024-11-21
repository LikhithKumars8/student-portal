from core.response_messages import field_not_null, field_not_blank, type_string, invalid_choice, invalid_url, invalid_integer_field, \
    invalid_email, required_fields_are_not_provided, invalid_foreign_key_id, code_has_to_be_unique
from rest_framework import exceptions
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
import re
from datetime import datetime

class FieldValidator:
    def validate(self, value):
        raise NotImplementedError

def is_valid_value(value, pattern):
    return re.match(pattern, value) is not None
  
class CharField(FieldValidator):
    """
        Custom function to validate a character field with choices.

        :param value: The value to validate.
        :param allow_null: Allow the value to be None.
        :param required: The field is required.
        :param allow_blank: Allow the value to be an empty string.
        :param choices: An optional list of allowed choices.
        :return: The processed value.
        :raises: ValueError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True, allow_blank=False, choices=None, regex=None, unique_code=None):
        self.allow_null = allow_null
        self.required = required
        self.allow_blank = allow_blank
        self.choices = choices
        self.regex  = regex
        self.unique_code = unique_code

    def validate(self, value):
        if value is None:
            if self.allow_null:
                return
            else:
                raise ValidationError(field_not_null)
        
        if value == '':
            if self.allow_blank:
                return
            elif not self.required:
                return
            else:
                raise ValidationError(field_not_blank)

        if not isinstance(value, str):
            raise ValidationError(type_string)

        value = value.strip()
        if self.choices is not None and value not in self.choices:
            raise ValidationError(invalid_choice)
        
        if self.regex is not None and not is_valid_value(value, self.regex):
            raise ValidationError(invalid_email)

        if self.unique_code and not self.unique_code(value):
            raise ValidationError(code_has_to_be_unique)
        return value


class URLField(FieldValidator):
    """
        Validate that the input value is a valid URL.
        
        :param value: The URL to validate.
        :raises ValidationError: If the URL is not valid.
    """
    def __init__(self, allow_null=False, required=True):
        self.allow_null = allow_null
        self.required = required

    def is_valid_url(self, url):
        """Check if the given string is a valid URL."""
        url_validator = URLValidator()
        try:
            url_validator(url)
            return True
        except DjangoValidationError:
            raise ValidationError(invalid_url)
    
    def validate(self, value):
        if value is None:
            if not self.allow_null:
                raise ValidationError(field_not_null)
        elif not self.is_valid_url(value):
            raise ValidationError(invalid_url)
        return value


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or {}


class BaseValidator:
    def __init__(self):
        self.fields = {}
        self.errors = {}

    def add_field(self, field_name, field_validator):
        self.fields[field_name] = field_validator

    def validate(self, data):
        self.errors = {}
        validated_data = {}
        for field_name, field_validator in self.fields.items():
            value = data.get(field_name)
            if field_validator.required and value == None:
                self.errors[field_name] = required_fields_are_not_provided
            try:
                validated_value = field_validator.validate(value)
                validated_data[field_name] = validated_value
            except ValidationError as e:
                self.errors[field_name] = str(e)

        if self.errors:
            raise exceptions.ValidationError({'errors': self.errors})
        return validated_data

class IntegerField(FieldValidator):
    """
        Custom function to validate a character field with choices.

        :param value: The value to validate.
        :param allow_null: Allow the value to be None.
        :param required: The field is required.
        :param allow_blank: Allow the value to be an empty .
        :param choices: An optional list of allowed choices.
        :return: The processed value.
        :raises: ValueError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True, choices=None, validator=None):
        self.allow_null = allow_null
        self.required = required
        self.choices = choices
        self.validator = validator

    def validate(self, value):
        value = str(value)
        if value is None:
            if self.allow_null:
                return
            else:
                raise ValidationError(field_not_null)
        if value == '':
            if not self.required:
                return
            else:
                raise ValidationError(field_not_blank)
        
        if value.isdigit() == False:
            raise ValidationError(invalid_integer_field)
        
        value = value.strip()
        if self.choices is not None and value not in self.choices:
            raise ValidationError(invalid_choice)
        
        if self.validator and not self.validator(value):
            raise ValidationError(invalid_foreign_key_id)
        return int(value) 
