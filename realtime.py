import asyncio
import websockets
import json

# AI
async def realtime_client():
    # 使用查询参数格式
    base_uri = "ws://localhost:8000/ws/realtime/"
    params = {
        "detial": "eeee",
        "usrid": "117"
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    uri = f"{base_uri}?{query_string}"
    
    async with websockets.connect(uri) as websocket:
   
        try:
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"缓存命中率: {data['缓存命中率']:.2%}")
                print(f"文章总浏览次数: {data['文章总浏览次数']}")
                print(f"用户浏览次数: {data['用户浏览次数']}")
                print(f"用户人数: {data['用户人数']}")
                print("=" * 50)
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"连接关闭: code={e.code}, reason={e.reason}")
        except KeyboardInterrupt:
            print("用户中断")
            # 发送关闭指令
            await websocket.close()

if __name__ == "__main__":
    asyncio.run(realtime_client())