import asyncio
from asyncio import Queue

class Test:
    def __init__(self):
        self.que = Queue()
        self.pue = Queue()
        
    async def consumer(self):
        while True:
            try:
                print('consumer',await self.que.get())
            finally:
                try:
                    self.que.task_done()    # 告知队列-1，不然join无法判断队列是否执行完毕
                except ValueError:  # 如果队列为空，再次调用task_done则会报错，ValueError('task_done() called too many times')，这里先捕获了，并判断队列是否为空
                    if self.que.empty():
                        print("que empty")         
                        
    async def work(self):
        while True:
            try:
                value = await self.pue.get()
                print('producer', value)
                await self.que.put(value)
            finally:
                try:
                    self.pue.task_done()    # 告知队列-1，不然join无法判断队列是否执行完毕
                except ValueError:  # 如果队列为空，再次调用task_done则会报错，ValueError('task_done() called too many times')，这里先捕获了，并判断队列是否为空
                    if self.pue.empty():
                        print("pue empty") 
                        
    async def run(self):
        await asyncio.wait([self.pue.put(i) for i in range(10)])
        tasks = [asyncio.ensure_future(self.work())]
        tasks.append(asyncio.ensure_future(self.consumer()))
        print('p queue join')
        await self.pue.join()
        print('p queue is done & q queue join')
        await self.que.join()
        print('q queue is done')
        for task in tasks:
            task.cancel()

            
#if__name__ =='__main__':
print('----start----')
case = Test()
loop = asyncio.get_event_loop()
loop.run_until_complete(case.run())
print('----end----')