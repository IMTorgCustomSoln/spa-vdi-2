from rest_framework import serializers

from api.models import Examiner, DocumentGroup, Document


class ExaminerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examiner
        fields = '__all__'

class DocumentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentGroup
        fields = '__all__'
        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        