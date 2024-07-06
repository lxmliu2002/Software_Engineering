from django import forms
import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class UploadFileForm(forms.Form):
    file = forms.FileField()


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            # 将文件保存到指定位置
            with open(os.path.join(settings.MEDIA_ROOT, file.name), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return JsonResponse({'code': 0, 'msg': 'success'})
        else:
            return JsonResponse({'code': -1, 'msg': '文件上传失败'})
    else:
        form = UploadFileForm()
        return JsonResponse({'code': 0, 'msg': 'success'})