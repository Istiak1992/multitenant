from rest_framework import serializers
from users.serializers import UserGenericSerializer
from .models import City, DistributorType, Distributor, DistributorWarning, WarningLog


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class DistributorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorType
        fields = ['id', 'name', 'description', 'photo', 'created', 'updated']
        depth = 1


class DistributorParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = [
            'id', 'name', 'created', 'updated'
        ]


class DistributorGenericSerializer(serializers.ModelSerializer):
    visit_frequency = serializers.CharField(source='get_visit_frequency_display')

    class Meta:
        model = Distributor
        fields = [
            'id', 'name', 'distributor_type', 'address', 'city', 'visit_frequency', 'language_preferences',
            'total_visits', 'ratings', 'created', 'updated'
        ]
        depth = 1


class DistributorListSerializer(serializers.ModelSerializer):
    distributor_parent = DistributorParentSerializer()
    distributor_user = UserGenericSerializer()
    account_manager = UserGenericSerializer()
    inspector = UserGenericSerializer()
    visit_frequency = serializers.CharField(source='get_visit_frequency_display')

    class Meta:
        model = Distributor
        fields = [
            'id', 'name', 'distributor_type', 'distributor_parent', 'address', 'city', 'location_lat', 'location_lng',
            'distributor_user', 'contact_name', 'contact_email', 'contact_mobile', 'contact_nationality',
            'account_manager', 'inspector', 'visit_frequency', 'language_preferences', 'sms_notification',
            'total_visits', 'ratings', 'created', 'updated'
        ]
        depth = 1


class DistributorCreateSerializer(serializers.ModelSerializer):
    location_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    location_lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)

    class Meta:
        model = Distributor
        fields = (
            'id', 'name', 'distributor_type', 'distributor_parent', 'address', 'city', 'location_lat', 'location_lng',
            'contact_name', 'contact_email', 'contact_mobile', 'contact_nationality',
            'account_manager', 'inspector', 'visit_frequency', 'language_preferences', 'sms_notification'
        )

    def create(self, validated_data):
        distributor = Distributor(**validated_data)
        distributor.save()

        return distributor


class DistributorDetailSerializer(serializers.ModelSerializer):
    distributor_parent = DistributorParentSerializer(read_only=True)
    distributor_user = UserGenericSerializer()
    account_manager = UserGenericSerializer(read_only=True)
    inspector = UserGenericSerializer(read_only=True)

    class Meta:
        model = Distributor
        fields = '__all__'
        depth = 1

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class DistributorWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorWarning
        fields = '__all__'
        depth = 2


class DistributorWarningLogSerializer(serializers.ModelSerializer):
    user = UserGenericSerializer()

    class Meta:
        model = WarningLog
        fields = [
            'distributor_warning', 'title', 'subtitle', 'generated_by', 'user', 'type',
            'action_name', 'action_type', 'created', 'updated'
        ]
        depth = 1
