# 🔍 Flowchart "NO" Branches Explained

Simple explanation of what happens when conditions are **NO (False)**.

---

## 📊 Decision Point 1: "Count >= 3?" (Proximity Stability)

```
    ┌───────────────┐
    │ Proximity     │
    │ Count++       │  ← Every time person is close, add 1
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Count >= 3?   │  ← Is person close for 3 times in a row?
    └───┬───────┬───┘
        │       │
    YES │       │ NO  ← What if NO?
        │       │
        ▼       │
┌───────────────┐│
│ Activate Face ││
│ Recognition   ││
└───────────────┘│
        │       │
        │       └─────────────────────────┐
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Go Back to    │
        │                         │ Main Loop     │
        │                         │ (Keep waiting)│
        │                         └───────┬───────┘
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Sleep 0.2s    │
        │                         └───────┬───────┘
        │                                 │
        │                                 └───┐
        │                                     │
        └─────────────────────────────────────┘
                    │
                    ▼
            Continue Main Loop
```

### What "NO" means here:
- **Person is close BUT not stable yet** (only 1 or 2 readings)
- **Action**: Don't activate face recognition yet
- **Why**: Prevents false triggers from noise or brief movements
- **Next**: Go back to main loop, keep checking distance

**Example:**
- Reading 1: 18cm ✅ (count = 1)
- Reading 2: 19cm ✅ (count = 2) 
- Reading 3: 25cm ❌ (person moved slightly, count resets)
- **Result**: NO, don't activate (not stable enough)

---

## 📊 Decision Point 2: "Away Count >= 4?" (Person Moved Away)

```
    ┌───────────────┐
    │ Away Count++  │  ← Every time person is far, add 1
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Count >= 4?   │  ← Is person away for 4 times in a row?
    └───┬───────┬───┘
        │       │
    YES │       │ NO  ← What if NO?
        │       │
        ▼       │
┌───────────────┐│
│ Turn OFF      ││
│ Lights        ││
└───────────────┘│
        │       │
        │       └─────────────────────────┐
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Keep Current  │
        │                         │ State         │
        │                         │ (Don't change)│
        │                         └───────┬───────┘
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Sleep 0.3s    │
        │                         └───────┬───────┘
        │                                 │
        │                                 └───┐
        │                                     │
        └─────────────────────────────────────┘
                    │
                    ▼
            Continue Main Loop
```

### What "NO" means here:
- **Person is away BUT not stable yet** (only 1, 2, or 3 readings)
- **Action**: Don't turn off lights yet, keep current state
- **Why**: Prevents flickering if person is moving in/out of range
- **Next**: Go back to main loop, keep checking

**Example:**
- Reading 1: 25cm ❌ (away_count = 1)
- Reading 2: 18cm ✅ (person came back, away_count resets)
- **Result**: NO, don't turn off lights (person might still be there)

---

## 📊 Decision Point 3: "Face Found?" (During Recognition)

```
    ┌─────────────────┐
    │ Detect Faces    │
    └────────┬────────┘
             │
             ▼
         ┌───────────────┐
         │ Face Found?   │  ← Did camera detect a face?
         └───┬───────┬───┘
             │       │
         YES │       │ NO  ← What if NO?
             │       │
             ▼       ▼
    ┌───────────────┐    ┌───────────────┐
    │ Process Face │    │ No Face       │
    │ (Largest)    │    │ Detected      │
    └───────────────┘    └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Lock          │
                         │ Recognition   │  ← Don't try again immediately
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Update Status │  ← Show "detecting" or "unknown"
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Go Back to    │
                         │ Main Loop     │
                         └───────────────┘
```

### What "NO" means here:
- **Camera didn't detect any face in the frame**
- **Action**: Lock recognition (don't retry immediately), update status
- **Why**: Person might be moving, looking away, or too far
- **Next**: Go back to main loop, wait for next proximity detection

**Example:**
- Person is close (15cm) ✅
- Camera captures frame
- Face detection runs
- **No face found** ❌ (person looking away, or too close/far)
- **Result**: NO, lock recognition, show "detecting" status

---

## 📊 Decision Point 4: "Confidence < 90 AND % > 70?" (Recognition Quality)

```
    ┌───────────────┐
    │ Map Confidence│
    └───────┬───────┘
            │
            ▼
         ┌───────────────┐
         │ Confidence <  │
         │ 90 AND % > 70?│  ← Is recognition good enough?
         └───┬───────┬───┘
             │       │
         YES │       │ NO  ← What if NO?
             │       │
             ▼       ▼
    ┌───────────────┐    ┌───────────────┐
    │ FACE          │    │ Low           │
    │ RECOGNIZED!   │    │ Confidence    │
    └───────────────┘    └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Unknown       │
                         │ Attempts++    │  ← Count failed attempts
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Attempts < 2? │
                         └───┬───────┬───┘
                             │       │
                         YES │       │ NO
                             │       │
                             ▼       ▼
                    ┌───────────────┐    ┌───────────────┐
                    │ Try Again     │    │ Handle as     │
                    │ (Go back to   │    │ Guest         │
                    │  main loop)   │    │               │
                    └───────────────┘    └───────────────┘
```

### What "NO" means here:
- **Face detected BUT confidence is too low** (bad match)
- **Action**: Increment unknown attempts counter
- **Why**: Prevents false positives from bad matches
- **Next**: 
  - If attempts < 2: Try again (go back to main loop)
  - If attempts >= 2: Treat as guest (unknown person)

**Example:**
- Face detected ✅
- LBPH confidence: 95 (too high = bad match)
- OR confidence %: 65% (too low)
- **Result**: NO, not a good match
- **Action**: Try 1 more time, then assign as guest if still fails

---

## 📊 Decision Point 5: "Timeout Elapsed?" (After Person Leaves)

```
    ┌───────────────┐
    │ Start 5s      │
    │ Timeout       │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Timeout       │  ← Has 5 seconds passed?
    │ Elapsed?      │
    └───┬───────┬───┘
        │       │
    YES │       │ NO  ← What if NO?
        │       │
        ▼       │
┌───────────────┐│
│ Final         ││
│ Cleanup       ││
└───────┬───────┘│
        │       │
        │       └─────────────────────────┐
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Keep Waiting  │
        │                         │ (Countdown)   │
        │                         └───────┬───────┘
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Update Status │
        │                         │ (Show waiting)│
        │                         └───────┬───────┘
        │                                 │
        │                                 ▼
        │                         ┌───────────────┐
        │                         │ Sleep 0.3s    │
        │                         └───────┬───────┘
        │                                 │
        │                                 └───┐
        │                                     │
        └─────────────────────────────────────┘
                    │
                    ▼
            Continue Main Loop
```

### What "NO" means here:
- **5 seconds haven't passed yet** (still in countdown)
- **Action**: Keep waiting, show countdown, update status
- **Why**: Gives time for person to return before final cleanup
- **Next**: Go back to main loop, check again

**Example:**
- Person moved away at 10:00:00
- Timeout started: 10:00:00
- Current time: 10:00:03
- **Result**: NO, only 3 seconds passed (need 5)
- **Action**: Keep waiting, show "waiting" status

---

## 🎯 Summary: What "NO" Always Means

In **ALL** decision points, "NO" means:

1. **Condition not met yet** (not stable, not ready, not good enough)
2. **Don't take action** (don't activate, don't turn off, don't recognize)
3. **Go back to main loop** (keep checking, wait for next iteration)
4. **Continue monitoring** (system keeps running, waiting for conditions to change)

---

## 🔄 The Pattern

```
    Check Condition
         │
         ▼
    ┌──────────┐
    │ Condition│
    │ Met?     │
    └───┬───┬──┘
        │   │
    YES │   │ NO
        │   │
        ▼   ▼
    Action  │
    (Do     │
     Something)│
        │   │
        │   └───► Go Back to Main Loop
        │         (Keep Waiting)
        │
        └───► Continue to Next Step
```

**Key Point**: "NO" is **NOT an error** - it's just "not ready yet". The system keeps checking until conditions are met!

---

## 💡 Real-World Example

**Scenario**: Person approaching the mirror

1. **Distance = 25cm** → Count = 1 → NO (not stable) → Keep checking
2. **Distance = 19cm** → Count = 2 → NO (not stable) → Keep checking  
3. **Distance = 18cm** → Count = 3 → **YES!** → Activate recognition
4. **Face detection** → No face → NO → Lock, update status
5. **Next loop** → Face found → Confidence 85% → **YES!** → Recognized!

The system is **patient** - it waits for stable conditions before acting!

