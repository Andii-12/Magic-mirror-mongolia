# 12V Single Relay Wiring Guide

## 🔌 **GPIO Pin Configuration**

| Component | Raspberry Pi Pin | GPIO Number | Physical Pin |
|-----------|------------------|-------------|--------------|
| Relay Control | GPIO 18 | 18 | Pin 12 |
| Ground | GND | - | Pin 6, 9, 14, 20, 25, 30, 34, 39 |

## ⚡ **Relay Module Connections**

### **12V Single Relay Module (e.g., SRD-05VDC-SL-C)**
```
VCC  → 5V (Pin 2 or 4) - Power for relay module
GND  → GND (Pin 6)     - Ground
IN   → GPIO 18 (Pin 12) - Control Pin
```

### **Relay Output Connections**
```
Relay Output (NO, COM, NC):
  - COM → 12V Power Supply Positive
  - NO  → Light Positive
  - NC  → Not used (or connect to different circuit)

12V Power Supply:
  - Positive → Relay COM terminal
  - Negative → Light negative (common ground)
```

## 🔧 **How It Works**

1. **GPIO Control**: 
   - `GPIO.HIGH` = Relay ON (lights on)
   - `GPIO.LOW` = Relay OFF (lights off)

2. **Proximity Detection**:
   - When ultrasonic sensor detects < 20cm → Lights turn ON
   - When ultrasonic sensor detects > 25cm → Lights turn OFF
   - 5cm buffer prevents flickering

3. **Safety Features**:
   - Lights automatically turn OFF on system shutdown
   - Error handling for GPIO failures
   - Status monitoring in debug output

## 🧪 **Testing**

Run the test script to verify relay functionality:
```bash
python3 scripts/test-relay.py
```

This will cycle the lights ON/OFF every 3 seconds.

## ⚠️ **Safety Notes**

1. **12V Power**: Use appropriate 12V power supply for your lights
2. **Relay Rating**: Ensure relay can handle your light's current draw
3. **Wiring**: Double-check all connections before powering on
4. **Fuses**: Consider adding fuses for protection
5. **Insulation**: Ensure all connections are properly insulated

## 🔍 **Troubleshooting**

- **Lights not turning on**: Check 12V power supply and relay connections
- **GPIO errors**: Verify pin connections and permissions
- **Flickering**: Adjust proximity buffer in code (currently 5cm)
- **Relay not working**: Check relay control pin connection
