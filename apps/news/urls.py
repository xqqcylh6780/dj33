from django.urls import path
from . import views

app_name = 'news'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.search, name='search'),
    path('news/',views.NewsListView.as_view(), name='news_list'),
    path('news/<int:news_id>/',views.News_detail.as_view(),name='news_detail'),
    path('news/banners/',views.BannerView.as_view(),name='banner'),
    path('news/<int:news_id>/comments/', views.CommentsView.as_view(), name='comments'),
]