import json

from django.core.paginator import Paginator
from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import render
import logging

logger = logging.getLogger('django')

# Create your views here.
from django.views import View

from utils.res_code import res_json, Code, error_map
from . import models
from .models import News


class IndexView(View):
    def get(self, request):
        tags = models.Tag.objects.only('name').filter(is_delete=False)
        hot = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url').order_by('priority')[0:3]
        click_hot = models.News.objects.only('title', 'image_url', 'update_time', 'author__username',
                                             'tag__name').select_related('tag').order_by('-clicks')[0:9]
        return render(request, 'news/index.html', locals())

class NewsListView(View):
    def get(self,request):
        try:
            tag_id = int(request.GET.get('tag_id',0))
        except Exception as e:
            logger.error('页面或标签定义错误\n{}'.format(e))
            tag_id = 0
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('页面或标签定义错误\n{}'.format(e))
            page = 1
        news_list = News.objects.values('title','digest','image_url','update_time','id').annotate(tag_name=F('tag__name'),author=F('author__username'))
        news = news_list.filter(tag_id=tag_id, is_delete=False) or news_list.filter(is_delete=False)

        pager = Paginator(news,5)
        try:
            news_info = pager.page(page)  # 拿到当前页返回
        except Exception as e:
            logger.error(e)
            news_info = pager.page(pager.num_pages)
        data = {
            'news': list(news_info),
            'total_pages': pager.num_pages
            }
        # return render(request,'news/index.html',context={'data':data})
        return res_json(data=data)


class News_detail(View):
    def get(self, request, news_id):
        news = models.News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name','author__username').filter(is_delete=False, id=news_id).first()

        comments = models.Comments.objects.select_related('author', 'parent').only('author__username', 'update_time','parent__update_time').filter(is_delete=False, news_id=news_id)
        comments_list = []
        for comm in comments:
            comments_list.append(comm.to_dict_data())
        if news:
            models.News.increase_clicks(news)
            return render(request, 'news/news_detail.html', locals())
        else:
            return HttpResponseNotFound('PAGE NOT FOUND')

class CommentsView(View):
    def post(self,request,news_id):
        if not request.user.is_authenticated:
            return res_json(errno=Code.SESSIONERR,errmsg=error_map[Code.SESSIONERR])

        if not models.News.objects.only('id').filter(is_delete=False,id=news_id).exists():
            return res_json(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])

        # 获取参数
        json_data = request.body
        if not json_data:
            return res_json(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])

        dita_data = json.loads(json_data)

        # 一级评论
        content = dita_data['content']
        if not dita_data.get('content'):
            return res_json(errno=Code.PARAMERR,errmsg='评论内容不能为空')

        # 回复评论
        parent_id = dita_data.get('parent_id')
        if parent_id:
            if not models.Comments.objects.only('id').filter(is_delete=False,id=parent_id,news_id=news_id).exists():
                return res_json(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        # 保存数据库
        news_content = models.Comments()
        news_content.content = content
        news_content.news_id = news_id
        news_content.author = request.user
        news_content.parent_id =parent_id if parent_id else None
        news_content.save()
        return res_json(data=news_content.to_dict_data())

class BannerView(View):
    def get(self,request):
        banner = models.Banner.objects.only('image_url','news__title').select_related('news').filter(is_delete=False).order_by('priority')  # 从1到6
        banner_info = []
        for i in banner:
            banner_info.append({
                'image_url': i.image_url,
                'news_title': i.news.title,
                'news_id': i.news.id
            })
        data = {
            'banners': banner_info
        }
        return res_json(data=data)

def search(request):
    return render(request, 'news/search.html')
