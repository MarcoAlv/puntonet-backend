import asyncio
from app.config import base
from redis import asyncio as redis
from app.utils.auth import claim_token
from contextlib import asynccontextmanager
from fastapi import WebSocket, WebSocketDisconnect
from app.core.db.sessionmanager import get_session
from typing import Any, AsyncGenerator, AsyncIterator


class ProtectedWebSocket:
    def __init__(self, ws: WebSocket):
        self._user = None
        self._error = {
            "type": "error",
            "payload": {
                "code": 401,
                "message": "Unauthorized"
            }
        }
        self._ws = ws

    async def accept(self, *args, **kwargs) -> None:
        await self._ws.accept(*args, **kwargs)
        try:
            data = await asyncio.wait_for(self._ws.receive_json(), timeout=12)
        except Exception:
            raise WebSocketDisconnect

        t_type = data.get("type", "")
        token = str(data.get("token", ""))
        if t_type != "authorization":
            print("no auth")
            raise WebSocketDisconnect
        async for db in get_session():
            try:
                user = await claim_token(
                        db=db,
                        token=token,
                        token_type="access"
                    )
            except ValueError:
                await self._ws.send_json(self._error)
                raise WebSocketDisconnect
            self._user = user.uuid
            break


class Event:
    def __init__(self, channel: str, message: str) -> None:
        self.channel = channel
        self.message = message

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Event) and self.channel == other.channel and self.message == other.message

    def __repr__(self) -> str:
        return f"Event(channel={self.channel!r}, message={self.message!r})"


class Unsubscribed(Exception):
    pass


class Subscriber:
    def __init__(self, queue: asyncio.Queue[Event | None]) -> None:
        self._queue = queue

    async def __aiter__(self) -> AsyncGenerator[Event | None, None]:
        try:
            while True:
                yield await self.get()
        except Unsubscribed:
            pass

    async def get(self) -> Event:
        item = await self._queue.get()
        if item is None:
            raise Unsubscribed()
        return item


class RedisBackend():
    _conn: redis.Redis

    def __init__(self, url: str | None = None, *, conn: redis.Redis | None = None):
        if url is None:
            assert conn is not None, "conn must be provided if url is not"
            self._conn = conn
        else:
            self._conn = redis.Redis.from_url(url, max_connections=base.BROKER_MAX_CONNECTIONS)

        self._pubsub = self._conn.pubsub()
        self._ready = asyncio.Event()
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._listener: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        self._listener = asyncio.create_task(self._pubsub_listener())
        await self._pubsub.connect()  # type: ignore[no-untyped-call]

    async def disconnect(self) -> None:
        await self._pubsub.aclose()  # type: ignore[no-untyped-call]
        await self._conn.aclose()
        if self._listener is not None:
            self._listener.cancel()

    async def subscribe(self, channel: str) -> None:
        self._ready.set()
        await self._pubsub.subscribe(channel)

    async def unsubscribe(self, channel: str) -> None:
        await self._pubsub.unsubscribe(channel)

    async def publish(self, channel: str, message: Any) -> None:
        await self._conn.publish(channel, message)

    async def next_published(self) -> Event:
        return await self._queue.get()

    async def _pubsub_listener(self) -> None:
        # redis-py does not listen to the pubsub connection if there are no channels subscribed
        # so we need to wait until the first channel is subscribed to start listening
        while True:
            await self._ready.wait()
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    event = Event(
                        channel=message["channel"].decode(),
                        message=message["data"].decode(),
                    )
                    await self._queue.put(event)

            # when no channel subscribed, clear the event.
            # And then in next loop, event will blocked again until
            # the new channel subscribed.Now asyncio.Task will not exit again.
            self._ready.clear()


class Broadcast:
    def __init__(self, url: str) -> None:
        self._backend = self._create_backend(url)
        self._subscribers: dict[str, set[asyncio.Queue[Event | None]]] = {}
        return

    def _create_backend(self, url: str) -> RedisBackend:
        return RedisBackend(url)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        await self._backend.connect()
        self._listener_task = asyncio.create_task(self._listener())

    async def disconnect(self) -> None:
        if self._listener_task.done():
            self._listener_task.result()
        else:
            self._listener_task.cancel()
        await self._backend.disconnect()

    async def _listener(self) -> None:
        while True:
            event = await self._backend.next_published()
            for queue in list(self._subscribers.get(event.channel, [])):
                await queue.put(event)

    async def publish(self, channel: str, message: Any) -> None:
        await self._backend.publish(channel, message)

    @asynccontextmanager
    async def subscribe(self, channel: str) -> AsyncIterator[Subscriber]:
        queue: asyncio.Queue[Event | None] = asyncio.Queue()

        try:
            if not self._subscribers.get(channel):
                await self._backend.subscribe(channel)
                self._subscribers[channel] = {queue}
            else:
                self._subscribers[channel].add(queue)

            yield Subscriber(queue)
        finally:
            self._subscribers[channel].remove(queue)
            if not self._subscribers.get(channel):
                del self._subscribers[channel]
                await self._backend.unsubscribe(channel)
            await queue.put(None)

broadcaster = Broadcast(url=base.BROKER_URL)
