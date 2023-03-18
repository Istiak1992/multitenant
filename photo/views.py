from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PhotoSerializer


class PhotoUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        photo_serializer = PhotoSerializer(data=request.data)

        if photo_serializer.is_valid():
            photo_serializer.save()
            return Response(data={
                'photo': photo_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(data={
                'errors': photo_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
