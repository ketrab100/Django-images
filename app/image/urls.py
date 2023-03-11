from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from .views import ImageViewSet

router = DefaultRouter()
router.register('', ImageViewSet, basename='Image')

urlpatterns = [
    path('', include(router.urls))
]
