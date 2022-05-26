from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.db.models import Q
from django.db.models import Max
from datetime import date, timedelta

import hashlib

from .models import User, auction_object, auction_participation, purchasing_execution
from .serialzers import User_Serializers, auction_object_Serializers, auction_object_Serializers_create, \
    purchasing_execution_Serializers, auction_participation_Serializers, \
    auction_participation_User_Serializers, purchasing_execution_User_Serializers

"""
    유저
"""


@api_view(['POST'])  # 로그인 유지
def user_check(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        search_cookie = data['accessToken']
        try:
            user = User.objects.get(cookie=search_cookie)
            if user.max_day < date.today():
                email = user.email
                new_nomel = email + str(date.today())
                new_nomel_base = hashlib.sha1(new_nomel.encode())
                user.accessToken = new_nomel_base.hexdigest()
                user.max_day = date.today() + timedelta(days=30)
                user.save()
                return Response({
                    "message": "토큰이 만료되었습니다."
                }, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "name": user.name,
                "money": user.money
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "message": "not found user"
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])  # 이메일 확인
def check_email(request):
    if request.method == "POST":
        serializer = JSONParser().parse(request)
        try:
            email = serializer['email']
            User.objects.get(email=email)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_200_OK)


@api_view(['POST'])  # 회원 가입
def user_create(request):
    if request.method == "POST":
        serializer = User_Serializers(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            email_base = hashlib.sha1(email.encode())
            serializer.save(accessToken=email_base.hexdigest(), max_day=date.today() + timedelta(days=30))
            return Response({
                "message": "생성 성공"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "생성 실패"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])  # 회원 수정, 삭제 , 조회
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            "message": "맞은 유저가 없습니다."
        }, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializers = User_Serializers(user)
        return Response(serializers.data)
    elif request.method == "PUT":
        serializer = User_Serializers(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        user.delete()
        return Response({
            "message": "유저가 삭제 되었습니다."
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])  # 로그인
def login(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        search_email = data['email']
        try:
            same_email = User.objects.get(email=search_email)
            if data['password'] == same_email.password:
                return Response({
                    "cookie": same_email.cookie
                }, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])  # 충전
def add_money(request, pk):
    if request.method == "POST":
        user = User.objects.get(pk=pk)
        money_add = JSONParser().parse(request)
        money = user.money + money_add['money']
        user.money = money
        serializer = User_Serializers(user)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])  # 판매 목록
def store_list(request, pk):
    if request.method == "GET":
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        list = auction_object.objects.filter(create_user=user)
        serializer = auction_object_Serializers(list, many=True)
        return Response(serializer.data)


"""
경매 등록
"""


@api_view(['GET'])  # 리스트
def Auction_list(request):
    if request.method == "GET":
        try:
            check_list = auction_object.objects.filter(
                term__range=[date.today() - timedelta(days=6), date.today()])
            for objects in check_list:
                try:
                    obj = auction_participation.objects.filter(
                        Q(auction_source=objects) and Q(auction_purchase=objects.max_money))
                    obj_user = objects.create_user
                    obj_user.money = obj_user.money + objects.max_money
                    for ob in obj:
                        obj_create = purchasing_execution(purchase_user=ob.auction_user,
                                                          purchase_source=ob.auction_source)
                        obj_create.save()
                except Exception:
                    pass
                objects.purchase_check = True
                objects.save()
            lists = auction_object.objects.filter(purchase_check=False)
            serializer = auction_object_Serializers(lists, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])  # 생성
def Auction_create(request):
    if request.method == "POST":
        serializer = auction_object_Serializers_create(data=request.data)
        if serializer.is_valid():
            create_id = serializer.validated_data.get('create_user')
            created = User.objects.get(pk=create_id)
            serializer.save(create_user=created)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])  # 조회 삭제
def Auction_detail(request, pk):
    try:
        auction = auction_object.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        try:
            money_object = auction_participation.objects.filter(auction_source=auction).aggregate(
                auction_purchase=Max('auction_purchase'))
            money = money_object['auction_purchase']
            auction.max_money = money
        except Exception:
            serializer = auction_object_Serializers(auction)
            return Response(serializer.data)
        auction.save()
        serializer = auction_object_Serializers(auction)
        return Response(serializer.data)
    elif request.method == "DELETE":
        auction.purchase_check = True
        auction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
    구매 
"""


@api_view(['POST'])  # 구매
def purchasing_create(request, pk):
    if request.method == "POST":
        try:
            serializer = purchasing_execution_Serializers(data=request.data)
            if serializer.is_valid():
                user_id = serializer.validated_data.get('purchase_user')
                user_ob = User.objects.get(pk=user_id)
                object_ob = auction_object.objects.get(pk=pk)
                user_ob.money = user_ob.money - object_ob.purchase
                if user_ob.money < 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                user = object_ob.create_user
                user.money = user.money + object_ob.purchase
                serializer.save(purchase_user=user_ob, purchase_source=object_ob)
                object_ob.purchase_check = True
                object_ob.save()
                user.save()
                user_ob.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])  # 구매 리스트 반환
def purchasing_list(request, pk):
    try:
        user = User.objects.get(pk=pk)
        list = purchasing_execution.objects.filter(purchase_user=user)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = purchasing_execution_User_Serializers(list, many=True)
        return Response(serializer.data)


"""
    경매 참여
"""


@api_view(['POST'])  # 경매 참여
def participation_create(request, pk):
    if request.method == "POST":
        try:
            serializer = auction_participation_Serializers(data=request.data)
            if serializer.is_valid():
                user_id = serializer.validated_data.get('auction_user')
                user_ob = User.objects.get(pk=user_id)
                object_ob = auction_object.objects.get(pk=pk)
                user_ob.money = user_ob.money - object_ob.auction
                if user_ob.money < 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                user_ob.save()
                serializer.save(auction_user=user_ob, auction_source=object_ob)
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])  # 경매 잠여 리스트
def participation_user_list(request, pk):
    try:
        user = User.objects.get(pk=pk)
        list = auction_participation.objects.filter(auction_user=user)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = auction_participation_User_Serializers(list, many=True)
        return Response(serializer.data)


@api_view(['DELETE'])  # 삭제
def participation_delete(request, pk):
    try:
        obj = auction_participation.objects.get(pk=pk)
    except auction_participation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        user = obj.auction_user
        user.money = user.money + obj.auction_purchase
        user.save()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
    편의
"""


@api_view(['POST'])
def search_list(request, search_text):
    if request.method == "POST":
        list = auction_object.objects.filter(Q(title__contains=search_text) or Q(content__contains=search_text))
        serializer = auction_object_Serializers(list, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def Kinds_search(request, search_text):
    if request.method == "POST":
        list = auction_object.ordering.filter(Kinds=search_text)
        serializer = auction_object_Serializers(list)
        return Response(serializer.data)
