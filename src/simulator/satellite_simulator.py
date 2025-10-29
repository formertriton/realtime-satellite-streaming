"""
Real-Time Satellite Telemetry Simulator
Generates realistic satellite orbital data for streaming system
"""
import numpy as np
import json
from datetime import datetime, timezone
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import time
from loguru import logger


@dataclass
class SatelliteState:
    """Represents the current state of a satellite"""
    satellite_id: int
    norad_id: int
    satellite_name: str
    timestamp: str
    latitude: float
    longitude: float
    altitude_km: float
    velocity_km_s: float
    x_pos_km: float
    y_pos_km: float
    z_pos_km: float
    vx_km_s: float
    vy_km_s: float
    vz_km_s: float
    orbital_period_min: float
    inclination_deg: float
    eccentricity: float

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class SatelliteSimulator:
    """
    Simulates realistic satellite telemetry data
    Uses simplified orbital mechanics with realistic parameters
    """
    
    # Earth parameters
    EARTH_RADIUS_KM = 6371.0
    EARTH_MU = 398600.4418  # km³/s² gravitational parameter
    
    # Satellite catalog with realistic parameters
    SATELLITE_CATALOG = [
        {"norad_id": 25544, "name": "ISS", "altitude": 420, "inclination": 51.6, "eccentricity": 0.0006},
        {"norad_id": 48274, "name": "STARLINK-1600", "altitude": 550, "inclination": 53.0, "eccentricity": 0.0001},
        {"norad_id": 43013, "name": "FENGYUN-4A", "altitude": 35786, "inclination": 0.1, "eccentricity": 0.0002},
        {"norad_id": 37849, "name": "METOP-C", "altitude": 817, "inclination": 98.7, "eccentricity": 0.0012},
        {"norad_id": 28654, "name": "GPS-BIIA-28", "altitude": 20180, "inclination": 55.0, "eccentricity": 0.0048},
        {"norad_id": 41866, "name": "LANDSAT-8", "altitude": 705, "inclination": 98.2, "eccentricity": 0.0001},
        {"norad_id": 39634, "name": "IRIDIUM-33-DEB", "altitude": 789, "inclination": 86.4, "eccentricity": 0.0015},
        {"norad_id": 43689, "name": "SENTINEL-3A", "altitude": 814, "inclination": 98.6, "eccentricity": 0.0008},
        {"norad_id": 25994, "name": "NOAA-15", "altitude": 807, "inclination": 98.5, "eccentricity": 0.0010},
        {"norad_id": 27424, "name": "ENVISAT-DEB", "altitude": 765, "inclination": 98.3, "eccentricity": 0.0020},
    ]
    
    def __init__(self, num_satellites: int = 10, noise_level: float = 0.05):
        """
        Initialize the satellite simulator
        
        Args:
            num_satellites: Number of satellites to simulate
            noise_level: Amount of noise to add (0-1)
        """
        self.num_satellites = min(num_satellites, len(self.SATELLITE_CATALOG))
        self.noise_level = noise_level
        self.satellites = self.SATELLITE_CATALOG[:self.num_satellites]
        
        # Initialize orbital parameters for each satellite
        self.orbital_phases = np.random.uniform(0, 2*np.pi, self.num_satellites)
        self.start_time = time.time()
        
        logger.info(f"Initialized simulator with {self.num_satellites} satellites")
    
    def _calculate_orbital_velocity(self, altitude_km: float) -> float:
        """Calculate orbital velocity using vis-viva equation"""
        radius = self.EARTH_RADIUS_KM + altitude_km
        velocity = np.sqrt(self.EARTH_MU / radius)
        return velocity
    
    def _calculate_orbital_period(self, altitude_km: float) -> float:
        """Calculate orbital period in minutes"""
        radius = self.EARTH_RADIUS_KM + altitude_km
        period_seconds = 2 * np.pi * np.sqrt(radius**3 / self.EARTH_MU)
        return period_seconds / 60.0
    
    def _calculate_position(self, 
                          altitude_km: float, 
                          inclination_deg: float, 
                          phase: float,
                          eccentricity: float) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate satellite position and velocity in ECI coordinates
        
        Returns:
            (x, y, z, vx, vy, vz) in km and km/s
        """
        # Semi-major axis
        a = self.EARTH_RADIUS_KM + altitude_km
        
        # Mean motion (rad/s)
        n = np.sqrt(self.EARTH_MU / a**3)
        
        # True anomaly (simplified, ignoring eccentricity for now)
        nu = phase
        
        # Distance from center
        r = a * (1 - eccentricity**2) / (1 + eccentricity * np.cos(nu))
        
        # Position in orbital plane
        x_orb = r * np.cos(nu)
        y_orb = r * np.sin(nu)
        z_orb = 0
        
        # Convert to ECI using inclination
        inc = np.radians(inclination_deg)
        x = x_orb
        y = y_orb * np.cos(inc)
        z = y_orb * np.sin(inc)
        
        # Velocity in orbital plane
        v = np.sqrt(self.EARTH_MU * (2/r - 1/a))
        vx_orb = -v * np.sin(nu)
        vy_orb = v * (np.cos(nu) + eccentricity)
        vz_orb = 0
        
        # Convert velocity to ECI
        vx = vx_orb
        vy = vy_orb * np.cos(inc)
        vz = vy_orb * np.sin(inc)
        
        return x, y, z, vx, vy, vz
    
    def _eci_to_lat_lon(self, x: float, y: float, z: float, timestamp: float) -> Tuple[float, float]:
        """
        Convert ECI coordinates to latitude/longitude
        
        Args:
            x, y, z: Position in ECI (km)
            timestamp: Unix timestamp
            
        Returns:
            (latitude, longitude) in degrees
        """
        # Earth rotation rate (rad/s)
        omega_earth = 7.2921159e-5
        
        # Greenwich hour angle
        gha = omega_earth * (timestamp - self.start_time)
        
        # Convert to geographic coordinates
        r = np.sqrt(x**2 + y**2 + z**2)
        latitude = np.degrees(np.arcsin(z / r))
        longitude = np.degrees(np.arctan2(y, x) - gha)
        
        # Normalize longitude to [-180, 180]
        longitude = ((longitude + 180) % 360) - 180
        
        return latitude, longitude
    
    def generate_telemetry(self) -> List[SatelliteState]:
        """
        Generate current telemetry for all satellites
        
        Returns:
            List of SatelliteState objects
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        timestamp = datetime.now(timezone.utc).isoformat()
        
        telemetry_data = []
        
        for i, sat in enumerate(self.satellites):
            # Update orbital phase based on orbital period
            period_sec = self._calculate_orbital_period(sat["altitude"]) * 60
            phase_rate = 2 * np.pi / period_sec
            current_phase = self.orbital_phases[i] + phase_rate * elapsed_time
            
            # Calculate position and velocity
            x, y, z, vx, vy, vz = self._calculate_position(
                sat["altitude"],
                sat["inclination"],
                current_phase,
                sat["eccentricity"]
            )
            
            # Add noise
            if self.noise_level > 0:
                noise = np.random.normal(0, self.noise_level, 6)
                x += noise[0]
                y += noise[1]
                z += noise[2]
                vx += noise[3] * 0.01
                vy += noise[4] * 0.01
                vz += noise[5] * 0.01
            
            # Calculate latitude/longitude
            lat, lon = self._eci_to_lat_lon(x, y, z, current_time)
            
            # Calculate altitude from position
            altitude = np.sqrt(x**2 + y**2 + z**2) - self.EARTH_RADIUS_KM
            
            # Calculate velocity magnitude
            velocity = np.sqrt(vx**2 + vy**2 + vz**2)
            
            # Calculate orbital period
            orbital_period = self._calculate_orbital_period(altitude)
            
            # Create satellite state
            state = SatelliteState(
                satellite_id=i + 1,
                norad_id=sat["norad_id"],
                satellite_name=sat["name"],
                timestamp=timestamp,
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                altitude_km=round(altitude, 2),
                velocity_km_s=round(velocity, 4),
                x_pos_km=round(x, 2),
                y_pos_km=round(y, 2),
                z_pos_km=round(z, 2),
                vx_km_s=round(vx, 4),
                vy_km_s=round(vy, 4),
                vz_km_s=round(vz, 4),
                orbital_period_min=round(orbital_period, 2),
                inclination_deg=round(sat["inclination"], 2),
                eccentricity=round(sat["eccentricity"], 4)
            )
            
            telemetry_data.append(state)
        
        return telemetry_data
    
    def generate_single_satellite(self, satellite_id: int) -> SatelliteState:
        """Generate telemetry for a single satellite"""
        all_telemetry = self.generate_telemetry()
        return all_telemetry[satellite_id - 1]


if __name__ == "__main__":
    # Test the simulator
    logger.info("Testing Satellite Simulator")
    
    sim = SatelliteSimulator(num_satellites=5, noise_level=0.02)
    
    # Generate telemetry
    for i in range(3):
        logger.info(f"\n--- Update {i+1} ---")
        telemetry = sim.generate_telemetry()
        
        for sat in telemetry:
            logger.info(f"{sat.satellite_name}: Alt={sat.altitude_km:.1f}km, "
                       f"Lat={sat.latitude:.2f}°, Lon={sat.longitude:.2f}°, "
                       f"Vel={sat.velocity_km_s:.2f}km/s")
        
        time.sleep(2)
    
    logger.info("\nSimulator test complete!")