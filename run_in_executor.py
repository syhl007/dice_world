import asyncio
import time
import threading

def ret(path, t=2):
    with open(path) as f:
        with open(path+'_bak', 'w') as w:
            for i in f.readlines():
                print(path, '||', threading.currentThread())
                print(path,'::',i)
                w.write(i+'\n')
                time.sleep(t)


async def get_text(index_url, t):
    try:
        print(index_url,",","1")
        loop = asyncio.get_event_loop()
        # 主要在这
        ## 然而up主错了，这里并没有进行协程的异步（虽然看起来像），但是当你打印任务执行的线程id时，会发现，其实这里是让线程池去执行任务，loop接收线程池执行结果，本质是多线程，而不是asyncio
        ## 详见：https://segmentfault.com/q/1010000007863971
        resp = await loop.run_in_executor(None, ret, index_url,t)
        print(index_url,",","2","-",resp)
    except Exception as err:
        # 出现异常重试
        print(err)
        traceback.print_exc()
        return None
    return resp

    
tasks = [get_text("G:/1.txt",6), get_text("G:/2.txt",2)]
# 获取EventLoop:
loop = asyncio.get_event_loop()
# 执行coroutine
start = time.time()
loop.run_until_complete(asyncio.wait(tasks))
end = time.time()
print("[loop time cost]", end - start)
start = time.time()
ret("G:/1.txt",6)
end = time.time()
print("[time cost 1]", end - start)
start = time.time()
ret("G:/2.txt",2)
end = time.time()
print("[time cost 2]", end - start)
#loop.close()
