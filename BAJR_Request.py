


import requests



def send_email(email, attacker,pre_rank,now_rank):
    # 设置请求的 URL 和参数
    content = f"你的竞技场排名发生变动！<br>攻击者：{attacker}<br>排名: {pre_rank}->{now_rank}<br><img src=\"http://124.221.41.97/junko.jpg\">"
    url = 'http://124.221.41.97:5151/BAJR/send'
    params = {
        'to': email,
        'message': content
    }
    response = requests.get(url, params=params)
    return response.text
