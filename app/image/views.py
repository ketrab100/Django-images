import os

from django.http import HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from .models import Image
from .serializers import ImageSerializer, ImageCreateSerializer, ImageLinkSerializer, ImageSimpleSerializer, ImageUpdateSerializer

from PIL import Image as PilImage


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ImageUpdateSerializer
        if self.action in ['retrieve']:
            return ImageSerializer
        if self.action == 'generate_link':
            return ImageLinkSerializer
        if self.action in ['create']:
            return ImageCreateSerializer
        return ImageSimpleSerializer

    def retrieve(self, request, pk=None):
        host = f"{request.scheme}://{request.get_host()}"
        try:
            image = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer_class()(
                image, context={'host': host})
            return Response(serializer.data)
        except:
            return Response("Image doesn't exist", status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # TODO remove static file
        # path = os.path.join(instance.image.name)
        # os.remove(path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        host = f"{request.scheme}://{request.get_host()}"
        if not request.user.tier.active_link_share:
            return Response('This method is not allowed in your plan', status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer_class()(data=request.data)
        return Response(serializer.generate_link(pk=pk, host=host))

    @action(detail=True, methods=['GET'], url_path=r'share/(?P<expire_time>\w+)', permission_classes=[permissions.AllowAny])
    def share(self, request, pk=None, expire_time=None):
        if datetime.strptime(expire_time, '%m%d%Y%H%M%S') < datetime.now():
            return Response('This link is expired', status.HTTP_400_BAD_REQUEST)
        imageInstance = Image.objects.get(pk=pk)
        image = PilImage.open(imageInstance .image)
        response = HttpResponse(content_type="image/jpeg")
        image.save(response, "JPEG")
        return response
