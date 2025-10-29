"""
Kafka Consumer for Real-Time Satellite Telemetry
Consumes and processes satellite data from Kafka
"""
import json
import sys
import os
from typing import Callable, Optional, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger
import time
from datetime import datetime


class SatelliteTelemetryConsumer:
    """
    Kafka consumer for processing satellite telemetry data
    """
    
    def __init__(self,
                 bootstrap_servers: str = 'localhost:9092',
                 topic: str = 'satellite-telemetry',
                 group_id: str = 'satellite-processor',
                 auto_offset_reset: str = 'latest'):
        """
        Initialize the Kafka consumer
        
        Args:
            bootstrap_servers: Kafka server address
            topic: Kafka topic name
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        
        # Statistics
        self.message_count = 0
        self.error_count = 0
        self.start_time = None
        
        # Initialize consumer
        self.consumer = None
        self._connect(auto_offset_reset)
        
        logger.info(f"Telemetry consumer initialized for topic '{topic}'")
    
    def _connect(self, auto_offset_reset: str):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                consumer_timeout_ms=1000  # Timeout for polling
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single telemetry message
        Override this method for custom processing
        
        Args:
            message: Telemetry data dictionary
            
        Returns:
            True if processing successful
        """
        # Default processing: just log the message
        satellite_name = message.get('satellite_name', 'Unknown')
        altitude = message.get('altitude_km', 0)
        latitude = message.get('latitude', 0)
        longitude = message.get('longitude', 0)
        
        logger.debug(
            f"Received: {satellite_name} - "
            f"Alt={altitude:.1f}km, Lat={latitude:.2f}°, Lon={longitude:.2f}°"
        )
        
        return True
    
    def consume_stream(self, 
                      message_handler: Optional[Callable[[Dict], bool]] = None,
                      max_messages: Optional[int] = None):
        """
        Consume messages from the stream
        
        Args:
            message_handler: Custom function to process messages
            max_messages: Maximum number of messages to process (None for infinite)
        """
        logger.info(f"Starting to consume from topic '{self.topic}'")
        
        self.start_time = time.time()
        handler = message_handler if message_handler else self.process_message
        
        try:
            for message in self.consumer:
                try:
                    # Extract the telemetry data
                    telemetry = message.value
                    
                    # Process the message
                    success = handler(telemetry)
                    
                    if success:
                        self.message_count += 1
                    else:
                        self.error_count += 1
                    
                    # Log progress every 100 messages
                    if self.message_count % 100 == 0:
                        self._log_statistics()
                    
                    # Check if we've reached the limit
                    if max_messages and self.message_count >= max_messages:
                        logger.info(f"Reached message limit of {max_messages}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.error_count += 1
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            raise
        finally:
            self._log_statistics(final=True)
            self.close()
    
    def _log_statistics(self, final: bool = False):
        """Log consumer statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        rate = self.message_count / elapsed if elapsed > 0 else 0
        
        prefix = "FINAL" if final else "Progress"
        logger.info(
            f"{prefix}: {self.message_count} messages processed "
            f"({rate:.1f} msg/s, {self.error_count} errors)"
        )
    
    def close(self):
        """Close the Kafka consumer"""
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed")


class TelemetryProcessor:
    """
    Example processor that stores telemetry data
    """
    
    def __init__(self):
        self.telemetry_buffer = []
        self.satellite_data = {}
        
    def process(self, telemetry: Dict[str, Any]) -> bool:
        """Process and store telemetry"""
        try:
            satellite_id = telemetry['satellite_id']
            satellite_name = telemetry['satellite_name']
            
            # Store in buffer
            self.telemetry_buffer.append(telemetry)
            
            # Update satellite tracking
            if satellite_id not in self.satellite_data:
                self.satellite_data[satellite_id] = {
                    'name': satellite_name,
                    'updates': 0,
                    'last_update': None
                }
            
            self.satellite_data[satellite_id]['updates'] += 1
            self.satellite_data[satellite_id]['last_update'] = telemetry['timestamp']
            
            # Log every 50 updates
            if len(self.telemetry_buffer) % 50 == 0:
                logger.info(f"Buffer size: {len(self.telemetry_buffer)} messages")
                logger.info(f"Tracking {len(self.satellite_data)} satellites")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in processor: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'total_messages': len(self.telemetry_buffer),
            'satellites_tracked': len(self.satellite_data),
            'satellite_data': self.satellite_data
        }


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Consume satellite telemetry from Kafka')
    parser.add_argument('--kafka-server', default='localhost:9092',
                       help='Kafka bootstrap server')
    parser.add_argument('--topic', default='satellite-telemetry',
                       help='Kafka topic name')
    parser.add_argument('--group-id', default='satellite-processor',
                       help='Consumer group ID')
    parser.add_argument('--max-messages', type=int, default=None,
                       help='Maximum messages to consume (None for infinite)')
    parser.add_argument('--offset', choices=['earliest', 'latest'], default='latest',
                       help='Starting offset position')
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    logger.info("=" * 60)
    logger.info("SATELLITE TELEMETRY CONSUMER")
    logger.info("=" * 60)
    logger.info(f"Kafka Server: {args.kafka_server}")
    logger.info(f"Topic: {args.topic}")
    logger.info(f"Group ID: {args.group_id}")
    logger.info(f"Offset: {args.offset}")
    logger.info(f"Max Messages: {args.max_messages or 'Infinite'}")
    logger.info("=" * 60)
    
    # Create processor
    processor = TelemetryProcessor()
    
    # Create and start consumer
    consumer = SatelliteTelemetryConsumer(
        bootstrap_servers=args.kafka_server,
        topic=args.topic,
        group_id=args.group_id,
        auto_offset_reset=args.offset
    )
    
    # Start consuming
    consumer.consume_stream(
        message_handler=processor.process,
        max_messages=args.max_messages
    )
    
    # Print final statistics
    stats = processor.get_statistics()
    logger.info("\n" + "=" * 60)
    logger.info("FINAL STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total messages processed: {stats['total_messages']}")
    logger.info(f"Satellites tracked: {stats['satellites_tracked']}")
    logger.info("\nPer-satellite updates:")
    for sat_id, data in stats['satellite_data'].items():
        logger.info(f"  {data['name']}: {data['updates']} updates")


if __name__ == "__main__":
    main()