from django.urls import path

from .views import check_email, user_create, user_detail, add_money, login, store_list \
    , Auction_list, Auction_create, Auction_detail, purchasing_create, participation_create \
    , search_list, participation_user_list, purchasing_list, participation_delete, user_check,Kinds_search

urlpatterns = [

    path('check_email/', check_email),
    path('user_crt/', user_create),
    path('user_dtl/<int:pk>', user_detail),
    path('add_mon/<int:pk>', add_money),
    path('login/', login),
    path('sto/list/<int:pk>', store_list),
    path('pur/list/<int:pk>', purchasing_list),
    path('par/user/list/<int:pk>', participation_user_list),

    path('Auc/list/', Auction_list),
    path('Auc/cre/', Auction_create),
    path('Auc/det/<int:pk>', Auction_detail),

    path('pur/cre/<int:pk>', purchasing_create),

    path('part/delt/<int:pk>', participation_delete),
    path('purt/cre/<int:pk>', participation_create),

    path('search=<str:search_text>', search_list),
    path('Kinds=<str:search_text>', Kinds_search),

    path('user_check/', user_check),
]
