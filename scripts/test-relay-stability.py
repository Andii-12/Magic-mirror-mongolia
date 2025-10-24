#!/usr/bin/env python3
"""
Test script for relay stability with simulated distance readings
Demonstrates the stability logic to prevent flickering
"""

import time
import sys

def simulate_distance_readings():
    """Simulate ultrasonic sensor readings that might cause flickering"""
    # Simulate readings around the 20cm threshold
    readings = [
        25, 22, 19, 18, 17, 16, 15,  # Getting closer
        16, 17, 18, 19, 20, 21, 22,  # Fluctuating around threshold
        23, 24, 25, 26, 27, 28, 29,  # Moving away
        30, 32, 35, 40, 45, 50,     # Far away
        45, 40, 35, 30, 28, 26, 24, # Coming back
        22, 20, 19, 18, 17, 16, 15, # Close again
    ]
    return readings

def test_stability_logic():
    """Test the stability logic without actual GPIO"""
    print("🧪 Testing Relay Stability Logic")
    print("=" * 40)
    print("Simulating distance readings around 20cm threshold")
    print("Lights should only change after 3 stable readings")
    print()
    
    # Stability parameters (same as in main code)
    PROXIMITY_THRESHOLD = 20
    LIGHTS_ON_STABLE_THRESHOLD = 3
    LIGHTS_OFF_STABLE_THRESHOLD = 3
    LIGHTS_OFF_BUFFER = 8
    
    # State variables
    lights_on = False
    lights_stable_count = 0
    lights_off_stable_count = 0
    
    readings = simulate_distance_readings()
    
    print("Distance | Lights | On_Stable | Off_Stable | Action")
    print("-" * 50)
    
    for i, distance in enumerate(readings):
        # Simulate the stability logic
        if distance <= PROXIMITY_THRESHOLD:
            lights_stable_count += 1
            lights_off_stable_count = 0
            
            if lights_stable_count >= LIGHTS_ON_STABLE_THRESHOLD and not lights_on:
                lights_on = True
                action = "TURN ON"
            else:
                action = f"Counting ON ({lights_stable_count}/{LIGHTS_ON_STABLE_THRESHOLD})"
        else:
            if distance > (PROXIMITY_THRESHOLD + LIGHTS_OFF_BUFFER):
                lights_off_stable_count += 1
                lights_stable_count = 0
                
                if lights_off_stable_count >= LIGHTS_OFF_STABLE_THRESHOLD and lights_on:
                    lights_on = False
                    action = "TURN OFF"
                else:
                    action = f"Counting OFF ({lights_off_stable_count}/{LIGHTS_OFF_STABLE_THRESHOLD})"
            else:
                # In buffer zone - maintain state
                lights_stable_count = 0
                lights_off_stable_count = 0
                action = "BUFFER ZONE"
        
        print(f"{distance:8.0f} | {'ON ' if lights_on else 'OFF'} | {lights_stable_count:9} | {lights_off_stable_count:10} | {action}")
        time.sleep(0.5)
    
    print("\n✅ Stability test completed!")
    print("Notice how lights only change after stable readings, preventing flickering.")

def main():
    """Main test function"""
    print("🔌 Relay Stability Test")
    print("This demonstrates how the stability logic prevents relay flickering")
    print()
    
    try:
        test_stability_logic()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
