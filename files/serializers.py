from rest_framework import serializers

from files.models import File


class FileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['id']


class FileRetrieveSerializer(serializers.ModelSerializer):

    presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_presigned_url(self, presigned_url) -> str:
        return self.instance.generate_download_presigned_url()


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = '__all__'


class DownloadPresignedUrlSerializer(serializers.Serializer):
    download_presigned_url = serializers.CharField()
