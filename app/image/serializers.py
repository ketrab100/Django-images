import os
from datetime import datetime, timedelta

from rest_framework import serializers
from .models import Image


class ImageSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name']


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name', 'image']


class ImageSerializer(serializers.ModelSerializer):
    original_image = serializers.SerializerMethodField(
        'get_original_image_link')

    thumbnail_links = serializers.SerializerMethodField('add_thumbnail_links')

    def get_original_image_link(self, image):
        if image.user.tier.unlimited_resolution:
            return f"{self.context.get('host')}{image.image.url}"
        return None

    def add_thumbnail_links(self, image):
        resolutions = []
        for resolution in image.user.tier.resolutions:
            resolutions.append(
                f"{self.context.get('host')}/images/{image.id}/thumbnail/{resolution}")
        return resolutions

    class Meta:
        model = Image
        fields = ['id', 'name', 'original_image', 'thumbnail_links']


class ImageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['name', 'image', 'user']
        extra_kwargs = {
            'image': {'required': 'True'}
        }


class ImageLinkSerializer(serializers.ModelSerializer):
    seconds = serializers.IntegerField()

    def generate_link(self, pk, host):
        if not self.is_valid():
            raise serializers.ValidationError(
                {'Seconds': 'Please enter a valid time.'})
        expire_date = datetime.now() + timedelta(seconds=self.data.get('seconds'))

        return f"{host}/images/{pk}/share/{expire_date.strftime('%m%d%Y%H%M%S')}"

    class Meta:
        model = Image
        fields = ['id', 'seconds']
        extra_kwargs = {
            'seconds': {'write_only': True},
        }
