from rest_framework import serializers


class PhoneNumberField(serializers.CharField):
    def to_representation(self, value):
        return str(value.mobile)
