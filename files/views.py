from django.shortcuts import render
from rest_framework import decorators, response, viewsets

from files import models
from files import serializers


class FileViewSet(viewsets.ModelViewSet):
    queryset =  models.File.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.FileCreateSerializer
        if self.action == 'retrieve':
            return serializers.FileRetrieveSerializer
        if self.action == 'download_presigned_url':
            return serializers.DownloadPresignedUrlSerializer
        return serializers.FileSerializer

    @decorators.action(detail=True, methods=['GET'], name='Get file download presigned url')
    def get_download_presigned_url(self, request, *args, **kwargs):
        instance = self.get_object()
        url = instance.generate_download_presigned_url()
        serializer = self.get_serializer({'download_presigned_url': url})
        return response.Response(serializer.data)
