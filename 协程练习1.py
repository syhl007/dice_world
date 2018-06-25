# Example of the queue how to work 
import asyncio
from asyncio import Queue

async def work(q):
     while True:
         i = await q.get()	# Queue的get为Coroutine
         try:
             print(i)
             print('q.qsize(): ', q.qsize())
         finally:
             q.task_done()	# 标志着取出的执行完毕，注意不是i.task_done()

			 
async def run():
    q = Queue()
    await asyncio.wait([q.put(i) for i in range(10)])	# 协程1，因为Queue的put为Coroutine，所以写入队列的数字不一定按顺序
    print("[q]",q)
    tasks = [asyncio.ensure_future(work(q))]	# 协程2，生成一个协程work对象处理列表Queue
    print("[tasks]", tasks)
    print('wait join')
    await q.join()	# 任务同步等待，若不等待，则会直接执行task.cancel()，导致没有任务执行。
    print('end join')
    for task in tasks:
        task.cancel()

		
		
#if__name__ =='__main__':
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
loop.close()