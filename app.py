import asyncio
from fastapi import FastAPI
import uvicorn
import contextlib
import time
import aiomqtt

mqtt_broker = None
mqtt_user = None
mqtt_pwd = None

max_handlers = 10  # 最大并发处理数量

sem = asyncio.Semaphore(max_handlers)

# mqtt client
client = None


async def subscribe_to_topic(client, topic):
        async with sem:
            await client.subscribe(topic,1)
            await asyncio.sleep(0.1)
            print(f"Subscribed to topic: {topic}")


async def message_consumer(message):
    async with sem:  # 使用异步上下文管理器获取信号量
        await asyncio.sleep(1)  # 模拟一个IO操作
        print(f"Received message on topic {message.topic}: {message.payload.decode()} 时间：{get_time()}")


def get_time():
    current_time = time.time()
    # 转换为本地时间的元组
    local_time = time.localtime(current_time)
    # 格式化时间
    return time.strftime('%Y-%m-%d %H:%M:%S', local_time)


async def run_mqtt():
    global client

    # 假设 模拟大量不同的topic
    topics = [
        "demo1",
        "demo2",
        "demo3",
        "demo4",
        "humidity",
        "demo6",
        "demo7",
        "demo8",
        "demo9",
        "temperature",
        "demo11",
        "demo12",
        "demo13",
        "demo14",
        "demo15",
        "demo16",
        "demo17",
        "pressure"
	]
    
    interval = 3  # Seconds

    while True:
        try:
            async with aiomqtt.Client(mqtt_broker,1883,username=mqtt_user,password=mqtt_pwd) as c:
                client = c
                await asyncio.gather(*[subscribe_to_topic(client, topic) for topic in topics])

                loop = asyncio.get_event_loop()
                async for message in c.messages:
                     loop.create_task(message_consumer(message))
        except aiomqtt.MqttError as e:
            print(f"断连错误: {e}; Reconnecting in {interval} seconds ...")
            await asyncio.sleep(interval)
    




"""
如果是多个任务 并发执行
    task_list = []
    for _ in range(10):
        task = asyncio.create_task(run_mqtt())
        task_list.append(task)
		
    asynclist =  asyncio.gather(*task_list)
    yield
    asynclist.cancel()

"""

# 上下文 + fastapi 生命周期
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        task = asyncio.create_task(run_mqtt())
        print("start----")
        yield
        task.cancel()
        print("end----")
    except asyncio.CancelledError or Exception as e:
            print(f"CancelledError {e}")
            

app = FastAPI(lifespan=lifespan)
   

@app.get("/status")
async def get_status():
    return "hello world"



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8082,lifespan='on')
