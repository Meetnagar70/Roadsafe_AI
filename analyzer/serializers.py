from rest_framework import serializers
from .models import AccidentReport

class AccidentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccidentReport
        fields = '__all__'
