"""
Test script for satellite simulator
Generates telemetry and saves to JSON files to demonstrate streaming capability
"""
import json
import time
import os
from datetime import datetime
from src.simulator.satellite_simulator import SatelliteSimulator
from loguru import logger

def main():
    # Create output directory
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("=" * 70)
    logger.info("REAL-TIME SATELLITE TELEMETRY STREAMING DEMO")
    logger.info("=" * 70)
    logger.info("Simulating 10 satellites with 1-second updates")
    logger.info("Data will be saved to JSON files in the 'data' directory")
    logger.info("=" * 70)
    
    # Initialize simulator
    sim = SatelliteSimulator(num_satellites=10, noise_level=0.02)
    
    # Stream for 30 seconds
    duration = 30
    interval = 1.0
    
    logger.info(f"Starting {duration}-second simulation...\n")
    
    all_data = []
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < duration:
            # Generate telemetry
            telemetry = sim.generate_telemetry()
            
            # Save each satellite's data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for sat in telemetry:
                # Add to collection
                all_data.append(sat.to_dict())
                
                # Log highlights
                if sat.satellite_id <= 3:  # Only log first 3 to avoid spam
                    logger.info(
                        f"[{sat.satellite_name:15}] "
                        f"Alt={sat.altitude_km:7.1f}km  "
                        f"Lat={sat.latitude:6.2f}°  "
                        f"Lon={sat.longitude:7.2f}°  "
                        f"Vel={sat.velocity_km_s:.2f}km/s"
                    )
            
            # Progress indicator
            elapsed = time.time() - start_time
            logger.info(f"--- {len(all_data)} total data points ({elapsed:.1f}s elapsed) ---\n")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    
    # Save all data to JSON file
    output_file = os.path.join(output_dir, f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    logger.info("\n" + "=" * 70)
    logger.info("SIMULATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total data points: {len(all_data)}")
    logger.info(f"Satellites tracked: 10")
    logger.info(f"Duration: {time.time() - start_time:.1f}s")
    logger.info(f"Output file: {output_file}")
    logger.info("=" * 70)
    
    # Show sample data structure
    logger.info("\nSample data point:")
    logger.info(json.dumps(all_data[0], indent=2))

if __name__ == "__main__":
    main()