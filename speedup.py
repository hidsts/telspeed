import requests
import random
import re
import time
import logging

logger = logging.basicConfig(level=logging.INFO, filename='info.log', datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s  %(levelname)s %(lineno)d --- [           %(name)s]  %(module)s  : %(message)s')
logger = logging.getLogger(__name__)

session = requests.session()

# 首先获取提速端口,服务端无响应线程会休眠5分钟再次获取
# 然后cookies中带ip字段访问提速接口
# ip中间的冒号必须用 %3A 替换
# ASCII Value ':'  -->  URL-encode '%3A'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

def get_nowtime():
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return nowtime

# 将格式字符串转换为时间戳
def strtime_to_int(s):
    result = time.mktime(time.strptime(s,"%Y-%m-%d %H:%M:%S"))
    return int(result)

def get_port():
    r = requests.get('http://ispeed.ebit.cn/speedup2/isCanSpeedup.jhtml', headers=headers, params={'r': random.uniform(0,1)}, timeout=5)
    port = r.cookies['ip']
    ports = port.replace(':','%3A')
    return port

def start():
    once = True
    while True:
        if once:
            once = False
            try:
                ip = get_port()
            except Exception as e:
                logger.error('远程服务器未响应')
                logger.error(e)
                time.sleep(300)
                once = True
                continue
            if not ip:
                logger.error('未获取到提速端口')
                break

        else:
            # ck = dict(userIds = '', userId = '', phone = '', phonedes = '', ip=ip)
            cks = {
                'ip': ip
            }
            r = session.get('http://ispeed.ebit.cn/speedup2/speedup.jhtml', headers=headers, cookies=cks)
            logger.info(r.text)
            if r.json()['state'] == 0:
                if '没有提速' in r.json()['message'] or '正在提速' in r.json()['message'] or '提速成功' in r.json()['message']:
                    content = r.content
                    content = content.decode('utf-8')
                    endtime = re.compile(r'endtime":"(.*?)"')
                    result = re.findall(endtime,content)
                    if result:
                        logger.info('提速成功！结束时间：' + result[0])
                        # 获得当前时间
                        t = get_nowtime()
                        # 获得提速结束时间和当前时间差，单位秒
                        tint = strtime_to_int(result[0] + ':00') - strtime_to_int(t)
                        # 线程睡眠
                        time.sleep(tint + 60)
                        # 提速结束后首先获取提速端口
                        once = True
                        continue
                    else:
                        logger.error('接口信息已更改')
                        break
                else:
                    logger.error('缺少参数')  
                    break
            else:
                logger.error('没有登陆或余额不足')  
                break


if __name__ == "__main__":
    start()
