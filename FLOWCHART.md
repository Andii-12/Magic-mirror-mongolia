# 🔄 Face Recognition System Flowchart

Complete flowchart of the MagicMirror² Face Recognition System.

---

## 📊 Main System Flow

```mermaid
flowchart TD
    Start([System Start]) --> Init[Initialize System]
    Init --> GPIO[Setup GPIO Pins<br/>- Ultrasonic: 23, 24<br/>- Relay: 18]
    GPIO --> LoadCascade[Load Face Cascade<br/>haarcascade_frontalface_default.xml]
    LoadCascade --> LoadTrainer[Load Trainer Model<br/>trainer.yml]
    LoadTrainer --> LoadLabels[Load Person Labels<br/>from Images/ directory]
    LoadLabels --> InitCamera[Initialize Camera<br/>Picamera2]
    InitCamera --> MainLoop[Main Loop Start]
    
    MainLoop --> ReadDistance[Read Ultrasonic Distance<br/>Median Filter 3 samples]
    ReadDistance --> CheckDistance{Distance <= 20cm?}
    
    CheckDistance -->|No| Away[Person Away]
    Away --> CheckAwayCount{Away Count >= 4?}
    CheckAwayCount -->|No| MainLoop
    CheckAwayCount -->|Yes| TurnOffLights[Turn OFF Relay Lights]
    TurnOffLights --> ClearPerson[Clear Person State]
    ClearPerson --> StartTimeout[Start 5s Timeout Timer]
    StartTimeout --> CheckTimeout{Timeout Elapsed?}
    CheckTimeout -->|No| MainLoop
    CheckTimeout -->|Yes| FinalCleanup[Final Cleanup]
    FinalCleanup --> MainLoop
    
    CheckDistance -->|Yes| Close[Person Close]
    Close --> ControlLights[Control Lights Based on Distance<br/>Schmitt Trigger Logic]
    ControlLights --> CheckProximityCount{Proximity Stable >= 3?}
    CheckProximityCount -->|No| MainLoop
    CheckProximityCount -->|Yes| Activate[Activate Face Recognition]
    Activate --> ResetState[Reset Recognition State]
    ResetState --> CheckRecognition{Recognition Attempted?}
    
    CheckRecognition -->|No| WaitDelay{Wait 0.3s?}
    WaitDelay -->|No| MainLoop
    WaitDelay -->|Yes| StartRecognition[Start Face Recognition]
    StartRecognition --> CaptureFrame[Capture Camera Frame]
    CaptureFrame --> DetectFaces[Detect Faces with Cascade]
    DetectFaces --> CheckFaces{Face Detected?}
    
    CheckFaces -->|No| NoFace[No Face Detected]
    NoFace --> LockRecognition[Lock Recognition]
    LockRecognition --> UpdateStatus[Update Status File]
    UpdateStatus --> MainLoop
    
    CheckFaces -->|Yes| ProcessFace[Process Largest Face<br/>Resize to 100x100<br/>Histogram Equalization]
    ProcessFace --> CheckRecognizer{Recognizer Available?}
    
    CheckRecognizer -->|No| NoRecognizer[No Recognizer]
    NoRecognizer --> HandleGuest[Handle as Guest<br/>Generate Guest Name]
    HandleGuest --> SaveGuestPhoto[Save Guest Skin Photo]
    SaveGuestPhoto --> UpdateStatus
    UpdateStatus --> MainLoop
    
    CheckRecognizer -->|Yes| PredictFace[Predict Face<br/>LBPH Recognizer]
    PredictFace --> CalculateConfidence[Calculate Confidence %<br/>Map LBPH to 0-100%]
    CalculateConfidence --> CheckConfidence{Confidence < 90<br/>AND<br/>Percent > 70%?}
    
    CheckConfidence -->|No| LowConfidence[Low Confidence Match]
    LowConfidence --> IncrementUnknown{Unknown Attempts < 2?}
    IncrementUnknown -->|Yes| MainLoop
    IncrementUnknown -->|No| HandleGuest
    
    CheckConfidence -->|Yes| Recognized[Face Recognized!]
    Recognized --> CopySkinPhoto[Copy Latest Skin Photo<br/>to Recognition Image]
    CopySkinPhoto --> SaveSkinPhoto[Save High-Res Skin Photo<br/>rpicam-still 1080x1080]
    SaveSkinPhoto --> TriggerAnalysis[Trigger Skin Analysis]
    TriggerAnalysis --> TurnOnLights[Turn ON Relay Lights]
    TurnOnLights --> LockRecognition[Lock Recognition]
    LockRecognition --> UpdateStatus[Update Status File<br/>with Person, Confidence, Image]
    UpdateStatus --> MainLoop
    
    style Start fill:#90EE90
    style Recognized fill:#FFD700
    style HandleGuest fill:#FFA500
    style TurnOffLights fill:#87CEEB
    style TurnOnLights fill:#FFD700
```

---

## 🔍 Detailed Sub-Processes

### 1. Face Recognition Process

```mermaid
flowchart LR
    A[Capture Frame] --> B[Convert RGB to BGR]
    B --> C[Convert to Grayscale]
    C --> D[Detect Faces<br/>Cascade Classifier]
    D --> E{Faces Found?}
    E -->|No| F[Return None]
    E -->|Yes| G[Select Largest Face]
    G --> H[Extract Face Region]
    H --> I[Resize to 100x100]
    I --> J[Histogram Equalization]
    J --> K[LBPH Predict]
    K --> L[Get Label & Confidence]
    L --> M[Map Confidence to %]
    M --> N{Good Match?}
    N -->|Yes| O[Return Person Name]
    N -->|No| P[Return Guest/None]
```

### 2. Skin Photo Capture Process

```mermaid
flowchart TD
    A[Face Recognized] --> B{Photo Already Saved<br/>This Session?}
    B -->|Yes| C{5 Minutes Passed?}
    C -->|No| D[Skip Photo]
    C -->|Yes| E[Allow New Photo]
    B -->|No| E
    E --> F[Stop Picamera2]
    F --> G[Wait 3s for Release]
    G --> H[Kill Camera Processes]
    H --> I[Use rpicam-still]
    I --> J[Capture 1080x1080 Photo]
    J --> K{Success?}
    K -->|No| L[Try Alternative Methods]
    L --> M[Fallback: ImageMagick]
    M --> N{Success?}
    N -->|No| O[Restart Picamera2]
    N -->|Yes| P[Save to Skin/PersonName/]
    K -->|Yes| P
    P --> Q[Trigger Skin Analysis]
    Q --> R[Restart Picamera2]
    R --> S[Return Success]
```

### 3. Relay Control Logic

```mermaid
flowchart TD
    A[Read Distance] --> B{Distance <= 20cm?}
    B -->|Yes| C[Increment ON Counter]
    C --> D{ON Counter >= 2?}
    D -->|Yes| E{Lights OFF?}
    E -->|Yes| F[Turn ON Lights]
    E -->|No| G[Keep ON]
    D -->|No| G
    F --> H[Set Block Timer 2s]
    G --> I[Update Status]
    H --> I
    
    B -->|No| J{Distance > 28cm?}
    J -->|Yes| K[Increment OFF Counter]
    K --> L{OFF Counter >= 5?}
    L -->|Yes| M{Lights ON?}
    M -->|Yes| N[Turn OFF Lights]
    M -->|No| O[Keep OFF]
    L -->|No| O
    N --> P[Set Block Timer 2s]
    O --> I
    P --> I
    I --> Q[Return]
```

### 4. Status File Update Flow

```mermaid
flowchart LR
    A[Determine Status Type] --> B{Person Close?}
    B -->|Yes| C{Person Recognized?}
    C -->|Yes| D[Status: recognized]
    C -->|No| E{Recognition Attempted?}
    E -->|No| F[Status: detecting]
    E -->|Yes| F
    B -->|No| G[Status: waiting]
    
    D --> H[Build Status JSON]
    F --> H
    G --> H
    
    H --> I[Include Fields:<br/>- person<br/>- distance<br/>- active<br/>- status<br/>- confidence<br/>- recognition_image<br/>- is_guest<br/>- log_messages]
    I --> J[Write to Temp File]
    J --> K[Atomic Rename]
    K --> L[Status File Updated]
```

### 5. System Initialization Flow

```mermaid
flowchart TD
    A[Start] --> B[Check Platform]
    B --> C{Windows?}
    C -->|Yes| D[Simulation Mode]
    C -->|No| E[Setup GPIO]
    E --> F{GPIO Success?}
    F -->|No| G[Continue Without GPIO]
    F -->|Yes| H[GPIO Ready]
    G --> I[Load Face Cascade]
    H --> I
    I --> J{Cascade Found?}
    J -->|No| K[Use Default Cascade]
    J -->|Yes| L[Load Custom Cascade]
    K --> M[Load Trainer Model]
    L --> M
    M --> N{Trainer Found?}
    N -->|No| O[No Recognizer]
    N -->|Yes| P[Trainer Loaded]
    O --> Q[Load Person Labels]
    P --> Q
    Q --> R[Initialize Variables]
    R --> S[System Ready]
    S --> T[Enter Main Loop]
```

---

## 📋 Key Decision Points

### Proximity Detection
- **Threshold**: 20cm
- **Stability**: Requires 3 consecutive readings
- **Away Detection**: Requires 4 consecutive readings

### Face Recognition
- **Confidence Threshold**: < 90 (LBPH) AND > 70% (mapped)
- **Unknown Attempts**: 2 attempts before assigning guest
- **Sticky Identity**: Maintains recognition for 8 seconds

### Relay Control
- **ON Threshold**: ≤ 20cm (2 stable readings)
- **OFF Threshold**: > 28cm (5 stable readings)
- **Debounce**: 2 second block timer

### Photo Capture
- **Interval**: 5 minutes minimum between photos
- **Resolution**: 1080x1080
- **Method**: rpicam-still (primary), ImageMagick (fallback)

---

## 🔄 State Machine

```
┌─────────────┐
│   WAITING   │ ← No person detected
└──────┬──────┘
       │ Distance < 20cm
       ▼
┌─────────────┐
│  DETECTING  │ ← Person close, recognizing
└──────┬──────┘
       │ Face recognized
       ▼
┌─────────────┐
│ RECOGNIZED  │ ← Person identified
└──────┬──────┘
       │ Distance > 20cm
       ▼
┌─────────────┐
│   TIMEOUT   │ ← 5 second countdown
└──────┬──────┘
       │ Timeout elapsed
       ▼
┌─────────────┐
│   WAITING   │
└─────────────┘
```

---

## 📝 Data Flow

```
┌─────────────────┐
│ Ultrasonic      │
│ Sensor (GPIO)   │──┐
└─────────────────┘  │
                     │
┌─────────────────┐  │
│ Camera          │──┤
│ (Picamera2)     │  │
└─────────────────┘  │
                     │
                     ▼
         ┌───────────────────┐
         │ face_recognition  │
         │ _system.py        │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │ Status File       │
         │ /tmp/magicmirror_ │
         │ face_status.json  │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │ Node Helper       │
         │ (facerecognition) │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │ Frontend Module   │
         │ (facerecognition) │
         └───────────────────┘
```

---

## 🎯 Main Loop Pseudocode

```
WHILE True:
    distance = get_distance()  # Median filtered
    control_lights(distance)
    
    IF distance <= 20cm:
        proximity_count++
        IF proximity_count >= 3 AND NOT active:
            activate_face_recognition()
        
        IF active AND person IS None AND NOT recognition_attempted:
            IF wait_time >= 0.3s:
                person = recognize_face()
                IF person:
                    save_skin_photo(person)
                    turn_on_lights()
                    lock_recognition()
        
        update_status_file()
        sleep(0.2s)
    ELSE:
        away_count++
        IF away_count >= 4:
            turn_off_lights()
            clear_person()
            start_timeout()
        
        IF timeout_elapsed:
            final_cleanup()
        
        update_status_file()
        sleep(0.3s)
```

---

## 🔧 Error Handling Flow

```mermaid
flowchart TD
    A[Operation] --> B{Success?}
    B -->|Yes| C[Continue]
    B -->|No| D[Log Error]
    D --> E{Recoverable?}
    E -->|Yes| F[Try Fallback]
    F --> G{Success?}
    G -->|Yes| C
    G -->|No| H[Use Default]
    E -->|No| H
    H --> I[Continue with Limited Functionality]
    I --> C
```

---

## 📊 Performance Optimizations

1. **Distance Smoothing**: Median filter (3 samples) + averaging
2. **Status Updates**: Throttled to 0.5s intervals
3. **Camera Reuse**: Single camera instance, not recreated
4. **Recognition Lock**: Prevents repeated attempts
5. **Relay Debouncing**: 2s block timer prevents flickering
6. **Photo Interval**: 5 minute minimum between captures

---

This flowchart represents the complete system architecture and data flow of the Face Recognition System.

