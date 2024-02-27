from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import ExaminerViewSet, DocumentGroupViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'users', ExaminerViewSet)
router.register(r'documentgroups', DocumentGroupViewSet)
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls))
]