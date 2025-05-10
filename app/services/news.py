import asyncio
from fastapi import WebSocket
from typing import List, Dict, Any
from app.schemas.news import News

import aio_pika
import json
import backoff
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.is_broadcasting = False
        self._broadcast_task = None
        self._rabbitmq_task = None
        self.exchange_name = "xbuddy.broadcast"
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.is_reconnecting = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"WebSocket connection established, current connection count: {len(self.active_connections)}")

        # Start RabbitMQ message listening task
        if not self._rabbitmq_task or self._rabbitmq_task.done():
            self.start_rabbitmq_listener()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.debug(f"WebSocket connection closed, current connection count: {len(self.active_connections)}")

            # If there are no connections, stop RabbitMQ listening
            if not self.active_connections and self._rabbitmq_task:
                self.stop_rabbitmq_listener()

    async def broadcast(self, message: Dict[str, Any]):
        if not self.active_connections:
            return  # If there are no active connections, return directly

        # Create a list of tasks to send messages asynchronously
        tasks = []
        disconnected_websockets = []

        for websocket in self.active_connections:
            try:
                # Add send task
                tasks.append(websocket.send_json(message))
            except Exception as e:
                logger.error(f"Sending message failed: {str(e)}")
                disconnected_websockets.append(websocket)

        # Wait for all send tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Remove disconnected WebSockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket)

    def start_rabbitmq_listener(self):
        """Start RabbitMQ message listening task"""
        self._rabbitmq_task = asyncio.create_task(self._rabbitmq_listener())
        logger.info("Starting RabbitMQ message listening task")

    def stop_rabbitmq_listener(self):
        """Stop RabbitMQ message listening task"""
        if self._rabbitmq_task and not self._rabbitmq_task.done():
            self._rabbitmq_task.cancel()
            self._rabbitmq_task = None
            logger.info("Stopping RabbitMQ message listening task")
            self.reconnect_attempts = 0

    # Use backoff library to create retry decorator
    @backoff.on_exception(
        backoff.expo,
        (aio_pika.exceptions.AMQPConnectionError, 
         aio_pika.exceptions.AMQPChannelError,
         ConnectionError,
         ConnectionRefusedError,
         OSError),
        max_tries=5,
        max_time=30,
        on_backoff=lambda details: logger.warning(
            f"RabbitMQ connection retry #{details['tries']}, waiting {details['wait']:.2f} seconds..."
        )
    )
    async def _establish_rabbitmq_connection(self):
        """Establish connection with RabbitMQ and return channel and exchange"""
        logger.info("Connecting to RabbitMQ")
        
        try:
            connection = await aio_pika.connect_robust(
                f"amqp://{self.rabbit_config['user']}:{self.rabbit_config['password']}@{self.rabbit_config['host']}:{self.rabbit_config['port']}/{self.rabbit_config['virtualhost']}",
                client_properties={
                    "connection_name": "xbuddy-websocket-client"
                }
            )
            
            # Create channel
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            
            # Declare exchange
            exchange = await channel.get_exchange(
                self.exchange_name
            )
            
            logger.info(f"Connected to RabbitMQ")
            return connection, channel, exchange
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise

    async def _rabbitmq_listener(self):
        """Listen for RabbitMQ messages and broadcast"""
        from app.config import get_config
        config = get_config()
        if "rabbit" not in config:
            logger.error("No RabbitMQ configuration found, unable to start listening")
            return
        
        self.rabbit_config = config["rabbit"]
        self.reconnect_attempts = 0
        
        while self.reconnect_attempts < self.max_reconnect_attempts and self.active_connections:
            try:
                # Establish connection
                connection, channel, exchange = await self._establish_rabbitmq_connection()
                
                async with connection:
                    # Declare temporary queue
                    queue = await channel.declare_queue(
                        name="",  # Empty name means temporary queue
                        exclusive=True,  # Exclusive queue
                        auto_delete=True  # Delete queue when connection is closed
                    )

                    await queue.bind(exchange)
                    
                    logger.debug(f"Queue bound to exchange {self.exchange_name}")
                    
                    # Reset reconnect count
                    self.reconnect_attempts = 0
                    
                    # Start consuming messages
                    async with queue.iterator() as queue_iter:
                        logger.info("Starting to listen for RabbitMQ messages")
                        try:
                            async for message in queue_iter:
                                async with message.process():
                                    try:
                                        # Parse message
                                        body = message.body.decode()
                                        logger.debug(f"Received message: {body[:50]}..." if len(body) > 50 else f"Received message: {body}")
                                        data = json.loads(body)
                                        
                                        # Convert to standard News format and broadcast
                                        if isinstance(data, dict):
                                            # Try to convert data to News model
                                            try:
                                                news = News(**data)
                                                await self.broadcast(news.model_dump())
                                                logger.debug(f"Broadcaster message: {news.title[:30]}...")
                                            except Exception as e:
                                                # If not compatible with News model, broadcast original data
                                                logger.warning(f"Message format is not compatible with News model: {str(e)}")
                                                await self.broadcast(data)
                                                logger.debug("Broadcasted custom format message")
                                        else:
                                            logger.warning(f"Received non-dictionary message: {type(data)}")
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to parse JSON message: {body[:50]}...")
                                    except Exception as e:
                                        logger.error(f"Handling message failed: {str(e)}")
                        except aio_pika.exceptions.ConnectionClosed:
                            logger.warning("RabbitMQ connection closed")
                            raise  # Re-raise exception to trigger reconnect
            except asyncio.CancelledError:
                logger.info("Listening task cancelled")
                break
            except Exception as e:
                self.reconnect_attempts += 1
                wait_time = min(30, 2 ** self.reconnect_attempts)  # Exponential backoff, longest wait 30 seconds
                
                logger.error(f"Listening loop failed: {str(e)}")
                logger.warning(f"Retry #{self.reconnect_attempts}/{self.max_reconnect_attempts} will be performed in {wait_time} seconds")
                
                # If there are still connections and retry count hasn't reached the limit, wait and retry
                if self.active_connections and self.reconnect_attempts < self.max_reconnect_attempts:
                    await asyncio.sleep(wait_time)
                else:
                    if self.reconnect_attempts >= self.max_reconnect_attempts:
                        logger.error(f"Reached maximum retry count ({self.max_reconnect_attempts}), stopping attempts")
                    break
        
        logger.info("Listening task ended")


# Create WebSocket connection manager instance
connection_manager = WebSocketConnectionManager()
