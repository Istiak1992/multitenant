from django.db.models import F
from rest_framework import serializers
from .models import (
    Checklist,
    Inspection,
    InspectionChecklist,
    InspectionNotification,
    InspectionLog
)
from users.serializers import UserGenericSerializer
from distributors.models import Distributor
from distributors.serializers import (
    DistributorDetailSerializer,
    DistributorGenericSerializer
)


class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = ['id', 'detail_en', 'distributor_type', 'created', 'updated']


class InspectionChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChecklist
        fields = ['id', 'detail_en', 'detail_ar', 'response', 'note', 'attachment']
        depth = 2


class InspectionChecklistUpdateSerializer(serializers.ModelSerializer):
    response = serializers.BooleanField(required=True)
    note = serializers.CharField(max_length=256, allow_null=True)

    class Meta:
        model = InspectionChecklist
        fields = ['id', 'response', 'note', 'attachment', 'updated']

    def validate(self, data):
        response = data.get('response')
        attachment = data.get('attachment')

        if not response and attachment is None:
            raise serializers.ValidationError("Attachment is required if response is false")

        return data


class InspectionGenericSerializer(serializers.ModelSerializer):
    distributor = DistributorGenericSerializer()
    inspector = UserGenericSerializer()

    class Meta:
        model = Inspection
        fields = [
            'id', 'serial_no', 'date_initial', 'distributor', 'total_mark', 'total_rating', 'inspector',
            'status', 'account_manager_image', 'finance_awb_image', 'created', 'updated'
        ]
        depth = 2


class InspectionListSerializer(serializers.ModelSerializer):
    distributor = DistributorGenericSerializer()
    inspector = UserGenericSerializer()
    account_manager = UserGenericSerializer()
    finance_manager = UserGenericSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Inspection
        fields = [
            'id', 'serial_no', 'date_initial', 'distributor', 'inspector', 'total_mark', 'total_rating',
            'account_manager', 'account_manager_image', 'account_is_read', 'finance_manager', 'finance_awb_image',
            'finance_awb_no', 'finance_record_no', 'finance_is_read', 'status', 'created', 'updated'
        ]
        depth = 2


class InspectionSerializer(serializers.ModelSerializer):
    distributor = DistributorGenericSerializer()
    inspector = UserGenericSerializer()
    account_manager = UserGenericSerializer()
    finance_manager = UserGenericSerializer()
    checklists = InspectionChecklistSerializer(many=True, required=False)

    class Meta:
        model = Inspection
        fields = [
            'id', 'serial_no', 'date_initial', 'distributor', 'inspector', 'total_mark', 'total_rating',
            'account_manager', 'account_manager_image', 'finance_manager', 'finance_awb_image', 'finance_awb_no',
            'finance_record_no', 'status', 'created', 'updated', 'checklists'
        ]
        depth = 2


class InspectionUpdateSerializer(serializers.ModelSerializer):
    checklists = InspectionChecklistUpdateSerializer(many=True)

    class Meta:
        model = Inspection
        fields = [
            'id', 'total_mark', 'total_rating', 'status', 'updated', 'checklists'
        ]

    def update(self, instance, validated_data):
        checklists_data = validated_data.pop('checklists')
        checklists = instance.checklists.all()
        checklists = list(checklists)

        full_marks = 0
        total_marks = 0
        total_rating = 0

        for checklist_data in checklists_data:
            photo = None

            if checklist_data['attachment']:
                photo = checklist_data['attachment']

            checklist = checklists.pop(0)
            checklist.response = checklist_data.get('response', checklist.response)
            checklist.note = checklist_data.get('note', checklist.note)
            checklist.attachment = photo
            checklist.save()

            full_marks += checklist.weight

            if checklist.response:
                total_marks += checklist.weight
                total_rating += 1

        instance.total_mark = total_marks / full_marks * 100 if full_marks else 0
        instance.total_rating = total_rating / len(checklists_data) * 10 if full_marks else 0
        instance.status = Inspection.STATUS_COMPLETED
        instance.save()

        # Update Distributor data
        Distributor.objects.filter(pk=instance.distributor.pk).update(
            total_visits=F('total_visits') + 1,
            ratings=(F('ratings') * F('total_visits') + instance.total_rating) / (F('total_visits') + 1)
        )

        return instance


class InspectionNotificationListSerializer(serializers.ModelSerializer):
    inspection = InspectionGenericSerializer()
    generated_by = UserGenericSerializer()

    class Meta:
        model = InspectionNotification
        fields = '__all__'
        depth = 2


class InspectionLogListSerializer(serializers.ModelSerializer):
    inspection = InspectionGenericSerializer()
    user = UserGenericSerializer()
    status = serializers.CharField(source='get_type_display')

    class Meta:
        model = InspectionLog
        fields = [
            'id', 'inspection', 'title', 'subtitle', 'generated_by', 'user', 'type', 'status', 'action_name',
            'action_type', 'created', 'updated'
        ]
        depth = 2


class InspectionLogUpdateSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = InspectionLog
        fields = '__all__'
