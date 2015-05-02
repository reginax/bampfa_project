from rest_framework import serializers
from datetime import datetime

class Image(object):
    def __init__(self, imagefilename, image, created=None):
        self.imagefilename = imagefilename
        self.image = image
        self.created = created or datetime.now()

class ImageSerializer(serializers.Serializer):
    imagefilename = serializers.CharField(max_length=200)
    image = serializers.ImageField()

    def create(self, validated_data):
        return Image(**validated_data)

    def update(self, instance, validated_data):
        instance.imagefilename = validated_data.get('imagefilename', instance.imagefilename)
        instance.image = validated_data.get('image', instance.image)
        return instance