# Гол Код - Ашиглах Заавар

## 📁 Файлууд

- **`main.py`** - Гол ажиллагааны код (задласан, хялбаршуулсан)
- **`face_recognition_system.py`** - Бүрэн систем (бүх функцтэй)

## 🚀 Хэрхэн ажиллуулах

### 1. Энгийн арга (main.py ашиглах)

```bash
# Windows дээр
python main.py

# Linux/Raspberry Pi дээр
python3 main.py
```

### 2. Test mode (камергүйгээр турших)

```bash
# Windows дээр
set FACE_RECOGNITION_TEST=true
python main.py

# Linux дээр
FACE_RECOGNITION_TEST=true python3 main.py
```

## 📋 Гол кодны бүтэц

### 1. Эхлүүлэх (Initialization)
```python
system = FaceRecognitionSystem()  # Систем үүсгэх
```
- GPIO эхлүүлэх
- Face recognition эхлүүлэх
- Камер эхлүүлэх

### 2. Гол цикл (Main Loop)
```python
system.run()  # Гол ажиллагаа
```

**Гол цикл дотор:**
1. Зайг унших (ultrasonic sensor)
2. Зайг жигд болгох (smoothing)
3. Baseline calibration
4. Гэрэл удирдах
5. Хүн ойртсон эсэхийг шалгах
6. Царай таних
7. Статус шинэчлэх

## 🔧 Тохиргоо

`main.py` файлын дээд хэсэгт тохиргоо байна:

```python
# GPIO pins
TRIG_PIN = 23
ECHO_PIN = 24
RELAY_PIN = 18

# Settings
PROXIMITY_THRESHOLD = 20  # cm
TIMEOUT_DELAY = 5  # seconds
```

## 📊 Гол функцүүд

| Функц | Тайлбар |
|-------|---------|
| `__init__()` | Систем эхлүүлэх |
| `run()` | **ГОЛ ЦИКЛ** - тасралтгүй ажиллана |
| `get_distance()` | Зайг унших |
| `recognize_face()` | Царай таних |
| `update_status_file()` | Статус файл шинэчлэх |
| `control_lights()` | Гэрэл удирдах |

## 🎯 Гол ажиллагааны урсгал

```
1. Эхлүүлэх (__init__)
   ↓
2. Гол цикл эхлэх (run)
   ↓
3. Зайг унших (get_distance)
   ↓
4. Хүн ойртсон эсэх? (distance <= threshold)
   ├─ Тийм → Царай таних (recognize_face)
   │           ↓
   │           Танигдсан? → Статус шинэчлэх
   │
   └─ Үгүй → Хүлээх
   ↓
5. Дахиад 3-р алхам руу буцах (while True)
```

## ⚠️ Анхаарах зүйлс

1. **Raspberry Pi дээр ажиллуулах:**
   - GPIO pins зөв холбогдсон байх
   - Камер идэвхжсэн байх
   - `trainer.yml` файл байх

2. **Windows дээр турших:**
   - `FACE_RECOGNITION_TEST=true` тохируулах
   - GPIO ажиллахгүй (загварчлагдсан)

3. **Алдаа гарвал:**
   - Log файлуудыг шалгах
   - GPIO холболтыг шалгах
   - Камерыг шалгах

## 📝 Жишээ

### Энгийн ажиллагаа:
```python
# main.py файлыг ажиллуулах
python main.py

# Гаралт:
# ============================================================
# Face Recognition System эхлэж байна...
# ✅ GPIO эхлүүлэгдлээ
# ✅ Cascade ачааллаа
# ✅ Trainer ачааллаа
# 🚀 Face Recognition System ажиллаж байна...
# 🎯 Хүн илрэв! (15.2cm)
# 📷 Царай таних эхэлж байна...
# ✅ Танигдлаа: Andii
```

## 🔗 Холбоотой файлууд

- `face_recognition_system.py` - Бүрэн систем
- `config/config.js` - MagicMirror тохиргоо
- `trainer.yml` - Сургасан царай
- `Images/` - Сургах зурагнууд

## ✅ Шалгах жагсаалт

- [ ] `main.py` файл байна
- [ ] Python 3.7+ суулгагдсан
- [ ] OpenCV суулгагдсан
- [ ] GPIO зөв холбогдсон (Raspberry Pi)
- [ ] Камер идэвхжсэн (Raspberry Pi)
- [ ] `trainer.yml` файл байна

---

**Амжилт хүсье! 🚀**

