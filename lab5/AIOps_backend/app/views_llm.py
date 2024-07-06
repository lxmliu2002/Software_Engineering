from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.http import JsonResponse
from openai import OpenAI
import time
import json

# def qwCompletion(model, messages, temperature, retry_times, round_sleep, fail_sleep, api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"):
@csrf_exempt
def qwCompletion(request):
    """千问接口

    Args:
        request (_type_): HTTP请求
        ```json
        {
            'model': 'qwen1.5-72b-chat',
            'messages': [],
            'api_key': 'sk-xxx',
            'temperature': 0.5,
            'retry_times': 3,
            'round_sleep': 1,
            'fail_sleep': 1,
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        }
        ```

    Returns:
        _type_: _description_
    """
    reqBody = json.loads(request.body.decode())
    model = reqBody.get('model', 'qwen1.5-72b-chat')
    messages = reqBody.get('messages', [])
    api_key = reqBody.get('api_key', 'sk-84952c1075734981a0e6b7cbfaae8bf4')
    temperature = reqBody.get('temperature', 0.5)
    retry_times = reqBody.get('retry_times', 3)
    round_sleep = reqBody.get('round_sleep', 1)
    fail_sleep = reqBody.get('fail_sleep', 1)
    base_url = reqBody.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
        )
    try:
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
    except Exception as e:
        print(e)
        for retry_time in range(retry_times):
            retry_time = retry_time + 1
            print(f"{model} Retry {retry_time}")
            time.sleep(fail_sleep)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                break
            except:
                continue

    model_output = response.choices[0].message.content.strip()
    time.sleep(round_sleep)

    return JsonResponse({'code': 0, 'msg': 'success', 'data': model_output})