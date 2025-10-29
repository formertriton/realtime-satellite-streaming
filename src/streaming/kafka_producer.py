"""
Kafka Producer for Real-Time Satellite Telemetry
Streams satellite data to Kafka topics
"""
import json
import time
import sys
import os
from typing import List, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator.satellite_simulator import SatelliteSimulator, SatelliteState


class SatelliteTelemetryProducer:
    """
    Kafka producer for streaming satellite telemetry data
    """
    
    def __init__(self, 
                 bootstrap_servers: str = 'localhost:9092',
                 topic: str = 'satellite-telemetry',
                 num_satellites: int = 10,
                 noise_level: float = 0.05):
        """
        Initialize the Kafka producer
        
        Args:
            bootstrap_servers: Kafka server address
            topic: Kafka topic name
            num_satellites: Number of satellites to simulate
            noise_level: Noise level for simulator
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        
        # Initialize simulator
        self.simulator = SatelliteSimulator(
            num_satellites=num_satellites,
            noise_level=noise_level
        )
        
        # Initialize Kafka producer
        self.producer = None
        self._connect()
        
        logger.info(f"Telemetry producer initialized for topic '{topic}'")
    
    def _connect(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1,
                compression_type='gzip'
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def send_telemetry(self, telemetry: SatelliteState) -> bool:
        """
        Send a single telemetry message to Kafka
        
        Args:
            telemetry: SatelliteState object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use satellite_id as the key for partitioning
            key = str(telemetry.satellite_id)
            value = telemetry.to_dict()
            
            # Send to Kafka
            future = self.producer.send(
                self.topic,
                key=key,
                value=value
            )
            
            # Wait for acknowledgment (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Sent telemetry for {telemetry.satellite_name} "
                f"(partition={record_metadata.partition}, offset={record_metadata.offset})"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending telemetry: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")
            return False
    
    def stream_telemetry(self, interval_sec: float = 1.0, duration_sec: Optional[float] = None):
        """
        Continuously stream telemetry data
        
        Args:
            interval_sec: Time between updates (seconds)
            duration_sec: Total duration to stream (None for infinite)
        """
        logger.info(f"Starting telemetry stream (interval={interval_sec}s)")
        
        start_time = time.time()
        message_count = 0
        error_count = 0
        
        try:
            while True:
                # Check duration limit
                if duration_sec and (time.time() - start_time) > duration_sec:
                    logger.info(f"Reached duration limit of {duration_sec}s")
                    break
                
                # Generate telemetry for all satellites
                telemetry_batch = self.simulator.generate_telemetry()
                
                # Send each satellite's telemetry
                for telemetry in telemetry_batch:
                    success = self.send_telemetry(telemetry)
                    if success:
                        message_count += 1
                    else:
                        error_count += 1
                
                # Log progress every 10 iterations
                if message_count % (10 * len(telemetry_batch)) == 0:
                    elapsed = time.time() - start_time
                    rate = message_count / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"Sent {message_count} messages "
                        f"({rate:.1f} msg/s, {error_count} errors)"
                    )
                
                # Wait for next interval
                time.sleep(interval_sec)
                
        except KeyboardInterrupt:
            logger.info("Stream interrupted by user")
        except Exception as e:
            logger.error(f"Error in streaming loop: {e}")
            raise
        finally:
            # Final statistics
            elapsed = time.time() - start_time
            logger.info(
                f"\nStreaming complete:\n"
                f"  Total messages: {message_count}\n"
                f"  Errors: {error_count}\n"
                f"  Duration: {elapsed:.1f}s\n"
                f"  Average rate: {message_count/elapsed:.1f} msg/s"
            )
            self.close()
    
    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            logger.info("Flushing and closing Kafka producer...")
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream satellite telemetry to Kafka')
    parser.add_argument('--kafka-server', default='localhost:9092',
                       help='Kafka bootstrap server')
    parser.add_argument('--topic', default='satellite-telemetry',
                       help='Kafka topic name')
    parser.add_argument('--num-satellites', type=int, default=10,
                       help='Number of satellites to simulate')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
    parser.add_argument('--duration', type=float, default=None,
                       help='Duration to stream in seconds (None for infinite)')
    parser.add_argument('--noise', type=float, default=0.05,
                       help='Noise level (0-1)')
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    logger.info("=" * 60)
    logger.info("SATELLITE TELEMETRY STREAMING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Kafka Server: {args.kafka_server}")
    logger.info(f"Topic: {args.topic}")
    logger.info(f"Satellites: {args.num_satellites}")
    logger.info(f"Interval: {args.interval}s")
    logger.info(f"Duration: {args.duration}s" if args.duration else "Duration: Infinite")
    logger.info("=" * 60)
    
    # Create and start producer
    producer = SatelliteTelemetryProducer(
        bootstrap_servers=args.kafka_server,
        topic=args.topic,
        num_satellites=args.num_satellites,
        noise_level=args.noise
    )
    
    # Start streaming
    producer.stream_telemetry(
        interval_sec=args.interval,
        duration_sec=args.duration
    )


if __name__ == "__main__":
    main()