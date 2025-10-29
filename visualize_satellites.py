"""
Real-Time 3D Satellite Visualization - Dark Mode
Shows satellites orbiting Earth with live updates
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from src.simulator.satellite_simulator import SatelliteSimulator
from loguru import logger
import time

# Set dark style globally
plt.style.use('dark_background')

class SatelliteVisualizer:
    """
    Real-time 3D visualization of satellite orbits
    """
    
    def __init__(self, num_satellites=10):
        self.simulator = SatelliteSimulator(num_satellites=num_satellites, noise_level=0.01)
        self.num_satellites = num_satellites
        
        # Get satellite names
        self.satellite_names = []
        
        # Setup the plot
        self.fig = plt.figure(figsize=(14, 10), facecolor='#0a0a0a')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='#0a0a0a')
        
        # Earth parameters
        self.earth_radius = 6371.0  # km
        
        # Initialize satellite plots
        self.satellite_plots = []
        self.orbit_trails = []
        self.satellite_positions = [[] for _ in range(num_satellites)]
        
        # Brighter colors for dark mode
        self.colors = plt.cm.viridis(np.linspace(0, 1, num_satellites))
        
        self._setup_plot()
        
    def _setup_plot(self):
        """Setup the 3D plot with Earth"""
        # Draw Earth with dark blue/teal color
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = self.earth_radius * np.outer(np.cos(u), np.sin(v))
        y = self.earth_radius * np.outer(np.sin(u), np.sin(v))
        z = self.earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        self.ax.plot_surface(x, y, z, color='#1e3d59', alpha=0.5, edgecolor='none')
        
        # Set labels and title with lighter colors
        self.ax.set_xlabel('X (km)', fontsize=10, color='white')
        self.ax.set_ylabel('Y (km)', fontsize=10, color='white')
        self.ax.set_zlabel('Z (km)', fontsize=10, color='white')
        self.ax.set_title('Real-Time Satellite Tracking System\n10 Satellites Orbiting Earth', 
                         fontsize=14, fontweight='bold', pad=20, color='white')
        
        # Set plot limits
        max_radius = 40000
        self.ax.set_xlim([-max_radius, max_radius])
        self.ax.set_ylim([-max_radius, max_radius])
        self.ax.set_zlim([-max_radius, max_radius])
        
        # Get initial telemetry to get names
        initial_telemetry = self.simulator.generate_telemetry()
        for sat in initial_telemetry:
            self.satellite_names.append(sat.satellite_name)
        
        # Initialize satellite markers
        for i in range(self.num_satellites):
            sat_plot, = self.ax.plot([], [], [], 'o', color=self.colors[i], 
                                     markersize=8, label=self.satellite_names[i])
            orbit_trail, = self.ax.plot([], [], [], '-', color=self.colors[i], 
                                        alpha=0.5, linewidth=1.5)
            self.satellite_plots.append(sat_plot)
            self.orbit_trails.append(orbit_trail)
        
        # Add legend with dark background
        legend = self.ax.legend(loc='upper right', fontsize=8, ncol=2, 
                               facecolor='#1a1a1a', edgecolor='#444444')
        plt.setp(legend.get_texts(), color='white')
        
        # Add grid with lighter color
        self.ax.grid(True, alpha=0.2, color='#444444')
        
        # Set pane colors
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
    def update(self, frame):
        """Update function for animation"""
        # Generate new telemetry
        telemetry = self.simulator.generate_telemetry()
        
        for i, sat in enumerate(telemetry):
            # Update position
            x, y, z = sat.x_pos_km, sat.y_pos_km, sat.z_pos_km
            
            # Store position for trail
            self.satellite_positions[i].append([x, y, z])
            
            # Keep only last 50 positions for trail
            if len(self.satellite_positions[i]) > 50:
                self.satellite_positions[i].pop(0)
            
            # Update satellite marker
            self.satellite_plots[i].set_data([x], [y])
            self.satellite_plots[i].set_3d_properties([z])
            
            # Update orbit trail
            if len(self.satellite_positions[i]) > 1:
                trail = np.array(self.satellite_positions[i])
                self.orbit_trails[i].set_data(trail[:, 0], trail[:, 1])
                self.orbit_trails[i].set_3d_properties(trail[:, 2])
        
        # Update title with frame number
        self.ax.set_title(
            f'Real-Time Satellite Tracking System\n'
            f'10 Satellites Orbiting Earth (Update #{frame+1})',
            fontsize=14, fontweight='bold', pad=20, color='white'
        )
        
        return self.satellite_plots + self.orbit_trails
    
    def animate(self, duration_sec=60, interval_ms=1000):
        """
        Start the animation
        
        Args:
            duration_sec: Duration to run animation
            interval_ms: Update interval in milliseconds
        """
        frames = int(duration_sec * 1000 / interval_ms)
        
        logger.info(f"Starting visualization for {duration_sec} seconds...")
        logger.info("Close the window to stop")
        
        anim = FuncAnimation(
            self.fig, 
            self.update, 
            frames=frames,
            interval=interval_ms,
            blit=False,
            repeat=True
        )
        
        plt.tight_layout()
        plt.show()


def create_static_visualization(num_satellites=10, duration_sec=10):
    """
    Create a static snapshot showing satellite positions
    """
    logger.info("Generating static visualization...")
    
    sim = SatelliteSimulator(num_satellites=num_satellites, noise_level=0.01)
    
    # Create figure with multiple views
    fig = plt.figure(figsize=(16, 10), facecolor='#0a0a0a')
    
    # 3D view
    ax1 = fig.add_subplot(221, projection='3d', facecolor='#0a0a0a')
    
    # Top view (XY plane)
    ax2 = fig.add_subplot(222, facecolor='#0a0a0a')
    
    # Side view (XZ plane)
    ax3 = fig.add_subplot(223, facecolor='#0a0a0a')
    
    # Altitude vs Time
    ax4 = fig.add_subplot(224, facecolor='#0a0a0a')
    
    # Collect data over time
    colors = plt.cm.viridis(np.linspace(0, 1, num_satellites))
    all_data = {i: {'x': [], 'y': [], 'z': [], 'alt': [], 'time': [], 'name': ''} 
                for i in range(num_satellites)}
    
    logger.info(f"Collecting {duration_sec} seconds of data...")
    start_time = time.time()
    
    while (time.time() - start_time) < duration_sec:
        telemetry = sim.generate_telemetry()
        current_time = time.time() - start_time
        
        for i, sat in enumerate(telemetry):
            all_data[i]['x'].append(sat.x_pos_km)
            all_data[i]['y'].append(sat.y_pos_km)
            all_data[i]['z'].append(sat.z_pos_km)
            all_data[i]['alt'].append(sat.altitude_km)
            all_data[i]['time'].append(current_time)
            all_data[i]['name'] = sat.satellite_name
        
        time.sleep(0.5)
    
    logger.info("Rendering visualization...")
    
    # Draw Earth in 3D view with dark blue
    earth_radius = 6371.0
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x_earth = earth_radius * np.outer(np.cos(u), np.sin(v))
    y_earth = earth_radius * np.outer(np.sin(u), np.sin(v))
    z_earth = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax1.plot_surface(x_earth, y_earth, z_earth, color='#1e3d59', alpha=0.5, edgecolor='#2a5a7a')
    
    # Draw Earth circles in 2D views
    theta = np.linspace(0, 2*np.pi, 100)
    x_circle = earth_radius * np.cos(theta)
    y_circle = earth_radius * np.sin(theta)
    ax2.plot(x_circle, y_circle, color='#2a5a7a', alpha=0.5, linewidth=2)
    ax3.plot(x_circle, y_circle, color='#2a5a7a', alpha=0.5, linewidth=2)
    ax2.fill(x_circle, y_circle, color='#1e3d59', alpha=0.3)
    ax3.fill(x_circle, y_circle, color='#1e3d59', alpha=0.3)
    
    # Plot satellite orbits
    for i in range(num_satellites):
        data = all_data[i]
        sat_name = data['name']
        
        # 3D view
        ax1.plot(data['x'], data['y'], data['z'], 
                color=colors[i], alpha=0.7, linewidth=2, label=sat_name)
        ax1.scatter(data['x'][-1], data['y'][-1], data['z'][-1], 
                   color=colors[i], s=120, marker='o', edgecolors='white', linewidths=0.5)
        
        # Top view (XY)
        ax2.plot(data['x'], data['y'], color=colors[i], alpha=0.7, linewidth=2)
        ax2.scatter(data['x'][-1], data['y'][-1], color=colors[i], s=120, marker='o', 
                   edgecolors='white', linewidths=0.5)
        
        # Side view (XZ)
        ax3.plot(data['x'], data['z'], color=colors[i], alpha=0.7, linewidth=2)
        ax3.scatter(data['x'][-1], data['z'][-1], color=colors[i], s=120, marker='o',
                   edgecolors='white', linewidths=0.5)
        
        # Altitude over time
        ax4.plot(data['time'], data['alt'], color=colors[i], 
                linewidth=2.5, label=sat_name, alpha=0.8)
    
    # Configure 3D view
    ax1.set_xlabel('X (km)', color='white')
    ax1.set_ylabel('Y (km)', color='white')
    ax1.set_zlabel('Z (km)', color='white')
    ax1.set_title('3D Orbital Paths', fontweight='bold', color='white', fontsize=12)
    legend1 = ax1.legend(fontsize=8, ncol=2, facecolor='#1a1a1a', edgecolor='#444444')
    plt.setp(legend1.get_texts(), color='white')
    ax1.grid(True, alpha=0.2, color='#444444')
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    
    # Configure top view
    ax2.set_xlabel('X (km)', color='white')
    ax2.set_ylabel('Y (km)', color='white')
    ax2.set_title('Top View (XY Plane)', fontweight='bold', color='white', fontsize=12)
    ax2.grid(True, alpha=0.2, color='#444444')
    ax2.axis('equal')
    
    # Configure side view
    ax3.set_xlabel('X (km)', color='white')
    ax3.set_ylabel('Z (km)', color='white')
    ax3.set_title('Side View (XZ Plane)', fontweight='bold', color='white', fontsize=12)
    ax3.grid(True, alpha=0.2, color='#444444')
    ax3.axis('equal')
    
    # Configure altitude plot
    ax4.set_xlabel('Time (seconds)', color='white')
    ax4.set_ylabel('Altitude (km)', color='white')
    ax4.set_title('Altitude Over Time', fontweight='bold', color='white', fontsize=12)
    legend4 = ax4.legend(fontsize=8, ncol=2, facecolor='#1a1a1a', edgecolor='#444444')
    plt.setp(legend4.get_texts(), color='white')
    ax4.grid(True, alpha=0.2, color='#444444')
    
    # Main title
    fig.suptitle('Real-Time Satellite Tracking System - Multi-View Analysis', 
                fontsize=16, fontweight='bold', color='white')
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'data/satellite_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    logger.info(f"Saved visualization to {output_file}")
    
    plt.show()


def main():
    """Main function with options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize satellite orbits')
    parser.add_argument('--mode', choices=['animated', 'static'], default='static',
                       help='Visualization mode')
    parser.add_argument('--satellites', type=int, default=10,
                       help='Number of satellites')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in seconds')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("SATELLITE ORBIT VISUALIZATION - DARK MODE")
    logger.info("=" * 70)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Satellites: {args.satellites}")
    logger.info(f"Duration: {args.duration}s")
    logger.info("=" * 70)
    
    if args.mode == 'animated':
        viz = SatelliteVisualizer(num_satellites=args.satellites)
        viz.animate(duration_sec=args.duration)
    else:
        create_static_visualization(
            num_satellites=args.satellites,
            duration_sec=args.duration
        )


if __name__ == "__main__":
    main()