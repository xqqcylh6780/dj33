from django.http import FileResponse, Http404
from django.shortcuts import render
import requests

# Create your views here.
from django.utils.encoding import escape_uri_path
from django.views import View

from dj33.settings import DOC_FILE_URL
from doc import models


def doc(request):
    docs = models.Doc.objects.only('image_url', 'desc', 'title').filter(is_delete=False)
    return render(request, 'doc/docDownload.html', context={'docs': docs})


class DocDownload(View):

    def get(self, request, doc_id):
        doc_file = models.Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc_file:
            doc_url = doc_file.file_url
            doc_url = DOC_FILE_URL + doc_url
            try:
                res = FileResponse(requests.get(doc_url, stream=True))
            except requests.exceptions.ConnectionError:
                res.status_code = 'connection fail'
            ex_name = doc_url.split('.')[-1]  # pdf

            if not ex_name:
                raise Http404('文件名异常')
            else:
                ex_name = ex_name.lower()

            if ex_name == 'pdf':
                res['Content-type'] = 'application/pdf'

            elif ex_name == 'doc':
                res['Content-type'] = 'application/msowrd'

            elif ex_name == 'ppt':
                res['Content-type'] = 'application/powerpoint'

            else:
                raise Http404('文件格式不正确')

            doc_filename = escape_uri_path(doc_url.split('/')[-1])

            # attachment  保存  inline 显示
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res

        else:
            raise Http404('文档不存在')

