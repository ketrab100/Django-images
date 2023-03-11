import os
from datetime import datetime, timedelta

from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    original_image = serializers.SerializerMethodField(
        'get_original_image_link')

    thumbnail_links = serializers.SerializerMethodField('add_thumbnail_links')

    def get_original_image_link(self, image):
        if image.user.tier.unlimited_resolution:
            return f"http://localhost:8000{image.image.url}"
        return None

    def add_thumbnail_links(self, image):
        print(os.environ.get('HOSTNAME'))
        resolutions = []
        for resolution in image.user.tier.resolutions:
            resolutions.append(
                f"http://localhost:8000/images/{image.id}/thumbnail/{resolution}")
        return resolutions

    class Meta:
        model = Image
        fields = ['name', 'original_image', 'thumbnail_links']


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['name', 'image', 'user']


class ImageLinkSerializer(serializers.ModelSerializer):
    seconds = serializers.IntegerField()

    def generate_link(self, pk):
        if not self.is_valid():
            return f"xd"
        expire_date = datetime.now() + timedelta(seconds=self.data.get('seconds'))

        return f"http://localhost:8000/images/{pk}/share/{expire_date.strftime('%m%d%Y%H%M%S')}"

    class Meta:
        model = Image
        fields = ['id', 'seconds']
        extra_kwargs = {
            'seconds': {'write_only': True},
        }
