from django.db import models

import uuid
import json


# Create your models here.
class DocumentGroup(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField()
    active = models.BooleanField(default=True)
    end_active_date = models.DateTimeField(null=True)
    bytes = models.IntegerField(default=0)


class Examiner(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    docgrp = models.ManyToManyField(DocumentGroup)
    
    def __str__(self):
        return self.name


class Document(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField()
    docgrp = models.ForeignKey(DocumentGroup, on_delete=models.CASCADE)
    bytes = models.IntegerField(default=0)
    metadata = models.TextField()
    uintarray = models.TextField()

    def set_metadata(self, data):
        self.metadata = json.dumps(data)

    def get_metadata(self):
        return json.loads(self.metadata)

    def set_array(self, arr):
        self.uintarray = json.dumps(arr)

    def get_array(self):
        return json.loads(self.uintarray)
    

'''TODO: 
class Note(models.Model):
    uuid = models.UUIDField()
    user_id = models.TextField()
    docgrp_id = models.TextField()
    note = models.TextField()

    
    

class UserDocGroup(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User.uuid)
    docgrp_id = models.ForeignKey(DocumentGroup.uuid)
'''