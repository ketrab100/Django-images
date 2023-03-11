from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from .models import Image
from .serializers import ImageSerializer, ImageCreateSerializer, ImageLinkSerializer

from PIL import Image as PilImage


class ImageViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'generate_link':
            return ImageLinkSerializer
        if self.action in ['create']:
            return ImageCreateSerializer
        return ImageSerializer

    @action(detail=True, methods=['GET'], url_path=r'thumbnail/(?P<resolution>\w+)',)
    def thumbnail(self, request, pk=None, resolution=None):
        if not float(resolution) in request.user.tier.resolutions:
            return Response('This heigth is not allowed in your plan', status.HTTP_400_BAD_REQUEST)

        imageInstance = self.get_queryset().get(pk=pk)
        image = PilImage.open(imageInstance .image)
        image.thumbnail((float(resolution), float(resolution)))
        response = HttpResponse(content_type="image/jpeg")
        image.save(response, "JPEG")
        return response

    @action(detail=True, methods=['POST'], url_path=r'generate_link',)
    def generate_link(self, request, pk=None):
        if not request.user.tier.active_link_share:
            return Response('This method is not allowed in your plan', status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer_class()(data=request.data)
        return Response(serializer.generate_link(pk=pk))

    @action(detail=True, methods=['GET'], url_path=r'share/(?P<expire_time>\w+)',)
    def share(self, request, pk=None, expire_time=None):
        if datetime.strptime(expire_time, '%m%d%Y%H%M%S') < datetime.now():
            return Response('This link is expired', status.HTTP_400_BAD_REQUEST)
        imageInstance = Image.objects.get(pk=pk)
        image = PilImage.open(imageInstance .image)
        response = HttpResponse(content_type="image/jpeg")
        image.save(response, "JPEG")
        return response
