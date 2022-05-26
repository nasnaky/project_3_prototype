from rest_framework import serializers
from .models import User, auction_object, auction_participation, purchasing_execution


class User_Serializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'money','Kinds','accessToken','max_day']
        read_only_field = ['id', 'money','accessToken','max_day']
        depth = 1


class auction_object_Serializers_create(serializers.ModelSerializer):
    create_user = serializers.IntegerField()

    class Meta:
        model = auction_object
        fields = ['id', 'title', 'content', 'img', 'purchase_check', 'purchase', 'auction', 'term', 'create_user','max_money',
                  'create_date']
        read_only_field = ['id', 'create_date','purchase_check','max_money']
        depth = 1


class auction_object_Serializers(serializers.ModelSerializer):
    create_user = serializers.StringRelatedField()

    class Meta:
        model = auction_object
        fields = ['id', 'title', 'content', 'img', 'purchase_check', 'purchase', 'auction', 'max_money', 'term',
                  'create_user', 'create_date']
        read_only_field = ['id', 'create_date']
        depth = 1


class auction_participation_Serializers(serializers.ModelSerializer):
    auction_user = serializers.IntegerField()
    auction_purchase = serializers.IntegerField()

    class Meta:
        model = auction_participation
        fields = ['id', 'auction_user', 'auction_source', 'auction_purchase']
        read_only_field = ['id']
        depth = 1


class auction_participation_User_Serializers(serializers.ModelSerializer):
    auction_user = serializers.StringRelatedField()
    auction_purchase = auction_object_Serializers

    class Meta:
        model = auction_participation
        fields = ['id', 'auction_user', 'auction_source', 'auction_purchase']
        read_only_field = ['id']
        depth = 1


class purchasing_execution_Serializers(serializers.ModelSerializer):
    purchase_user = serializers.IntegerField()
    purchase_source = serializers.IntegerField()

    class Meta:
        model = purchasing_execution
        fields = ['id', 'purchase_user', 'purchase_source']
        read_only_field = ['id']
        depth = 1


class purchasing_execution_User_Serializers(serializers.ModelSerializer):
    purchase_user = serializers.StringRelatedField()
    purchase_source = auction_object_Serializers

    class Meta:
        model = purchasing_execution
        fields = ['id', 'purchase_user', 'purchase_source']
        read_only_field = ['id']
        depth = 1
