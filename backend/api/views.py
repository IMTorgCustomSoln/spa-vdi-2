#from django.shortcuts import render
from rest_framework import viewsets

from api.models import Examiner, DocumentGroup, Document
from api.serializers import ExaminerSerializer, DocumentGroupSerializer, DocumentSerializer


# Create your views here.
class ExaminerViewSet(viewsets.ModelViewSet):
    queryset = Examiner.objects.all()
    serializer_class = ExaminerSerializer 

class DocumentGroupViewSet(viewsets.ModelViewSet):
    queryset = DocumentGroup.objects.all()
    serializer_class = DocumentGroupSerializer 
    '''
    #TODO: perform all ops in orm
    #[ref](https://stackoverflow.com/questions/58406804/list-object-has-no-attribute-model)
    groups = DocumentGroup.objects.all()
    new_groups = []
    for group in groups:
        bytes = sum([grp.bytes for grp in group.document_set.all()])
        group.bytes = bytes
        new_groups.append(group)
    queryset = new_groups
    serializer_class = DocumentGroupSerializer
    '''
    
    
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer 