from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework import status
from .models import (Nationality, Fine)
from .serializers import (NationalitySerializer, FineSerializer)


class NationalityListAPIView(ListAPIView):
    queryset = Nationality.objects.all()
    serializer_class = NationalitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'message': 'Success',
            'nationalities': serializer.data,
        }, status=status.HTTP_200_OK)


class FineListAPIView(ListAPIView):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'message': 'Success',
            'fines': serializer.data,
        }, status=status.HTTP_200_OK)
