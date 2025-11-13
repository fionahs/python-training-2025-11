import time
import threading
import asyncio

def fake_blocking_io_task(name):
    print(f"{name} start blocking I/O task")
    time.sleep(2)
    print(f'{name} done')

async def fake_non_blocking_IO_task(name):
    print(f"{name} start async I/O task")
    await asyncio.sleep(2)
    asyncio.to_thread()
    print(f'{name} done')
    
def execute_blocking_tasks():
    start = time.time()
    for i in range(5):
        fake_blocking_io_task(f"task - {i}")
        
    print(f"[Blocking] Total time {time.time() - start:.2f} seconds")
        
# execute_blocking_tasks()

# I/O bounding tasks: sleep, read Database, make api call to to other service
# CPU bound tasks: cpu calculation heavy task

# GIL (Global Interpreter lock) - limit only one thread is running in python

def cpu_task():
    print(f'calculating')
    pow(365, 1000000) # take about 1s
    print('done')

def threading_run():
    threads = []
    start = time.time()
    for i in range(5):
        # t = threading.Thread(target=fake_blocking_io_task, args=(f"task - {i}",))
        t = threading.Thread(target=cpu_task)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"[Threading] Total time {time.time() - start:.2f} seconds")
    
# threading_run()
# threading_run()
# multi thread vs multi process


async def async_run():
    start = asyncio.get_event_loop().time()
    await asyncio.gather(*[fake_non_blocking_IO_task(f"task {i}") for i in range(5)])
    print(f"[async run] Total time { asyncio.get_event_loop().time() - start:.2f} seconds")
    
asyncio.run(async_run())



