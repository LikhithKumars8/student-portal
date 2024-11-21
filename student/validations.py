# Custom validators
from core.validators import BaseValidator, CharField, IntegerField

class StudentValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self.add_field('name', CharField(allow_blank=False))
        self.add_field('subject', IntegerField(allow_null=False))
        self.add_field('marks', IntegerField(allow_null=False))
