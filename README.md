# awesome-python
records awesome py IOT project

### aiomqtt + fastapi 【app.py】

#### 是什么？  
本例子 主要是适用于工业IOT场景，需要消费大量实时工艺数据,使用深度模型预测性监控工艺的合格度，从而提高产品品控，减少人力投入，提高ROI指标  
#### 为什么？  
为什么使用python？因为很多深度模型需要python；需要一个后台服务，所以写了基于fastapi服务 + aiomqtt 异步消费mqtt
#### 怎么做?  
1.使用asyncio 异步协程 处理高并发问题  
@contextlib.asynccontextmanager 允许你通过定义异步上下文管理器，在不同生命周期阶段执行特定的异步操作。在 FastAPI 的 lifespan 中使用这种方式，可以确保在应用程序启动和关闭时，能够按照预期地管理异步任务和资源
在异步函数中，yield 通常结合 asyncio 的相关方法使用，用于暂停当前函数的执行，并将控制权返回给事件循环（event loop）
yield之后 类似于 before unmounted Server【服务卸载之前】执行的操作

```python3
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        task = asyncio.create_task(run_mqtt())
        yield
        task.cancel()
    except Exception as e:
            print(f"Task cancelled {e}")
            

app = FastAPI(lifespan=lifespan)

```


2.mqtt 使用 aiomqtt 异步订阅topic，mqtt 订阅topic 和 发送端 最好使用 Qos 为 1；提高消息接收率,mqtt Qos如下  
```txt
QoS 0 - 最多一次传递（At most once）：
这是最低的服务质量级别，消息发布者发送消息后，不会收到任何确认。消息可能会丢失或重复，也没有重新传输的机制。适用于实时性要求不高，且消息丢失或重复对系统影响不大的场景。
QoS 1 - 至少一次传递（At least once）：
在这个级别下，消息发布者会收到一个确认（PUBACK）消息，确保消息至少被传递一次给订阅者。如果发布者没有收到确认，它会重新发送消息，这样可以确保消息最终被接收。这种确认机制保证了消息不会丢失，但可能会导致消息重复
QoS 2 - 刚好一次传递（Exactly once）：
这是最高的服务质量级别，确保消息被精确地传递一次。在 QoS 2 中，除了发布者和订阅者之间的确认（PUBREC、PUBREL 和 PUBCOMP）外，还使用了消息排重和顺序控制。虽然 QoS 2 提供了最高的可靠性，但由于需要更多的通信开销和处理，因此它可能会导致一些性能损失。
```

3.使用async with 异步编程中处理上下文管理器，自动处理资源释放，降低了资源泄漏的风险

```python3
   while True:
        try:
            async with aiomqtt.Client('10.165.39.69',1883,username='admin',password='mop666666') as c:
                client = c
                await asyncio.gather(*[subscribe_to_topic(client, topic) for topic in topics])

                loop = asyncio.get_event_loop()
                async for message in c.messages:
                     loop.create_task(foo(message))
        except aiomqtt.MqttError as e:
            print(f"Connection lost due to {e}; Reconnecting in {interval} seconds ...")
            await asyncio.sleep(interval)

```

4.关于并发问题方面，使用 asyncio.Semaphore(10) + asyn with 【异步上下文】 来解决并发问题，如果1秒钟有20条数据，我们可以控制并发数 使用 asyncio 强大的协程并发能力 处理大量消费数据 效率极高
```python3
async def subscribe_to_topic(client, topic):
        async with sem:
            await client.subscribe(topic)
            await asyncio.sleep(0.1)
            print(f"Subscribed to topic: {topic}")
        

async def message_consumer(client):
    async for message in client.messages:
        asyncio.create_task(foo(sem,message))

```

5.深度学习 【代码暂时不展示】
主要使用 数据增强 做数据集，多分类的思想 训练模型，然后构建网络骨架 在fastapi 服务内消费 和判断 工艺曲线数据的合格率


6.fastapi 这里主要做 实时数据的接口 利用发布订阅 + Server-Sent Events 技术，单向主推 替代的沉重的双向长连接websocket  以及飞书api 机器人报警服务的推送等功能 和 数据归档落库逻辑


【未完待续...】
