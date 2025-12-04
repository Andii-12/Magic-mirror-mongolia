# Хэрхэн Ашиглах - Бүтэн Систем vs Main.py

## ⚠️ Чухал Мэдээлэл

### `main.py` vs `face_recognition_system.py`

| Файл | Тайлбар | Ашиглах |
|------|---------|---------|
| **`main.py`** | Зөвхөн задласан, хялбаршуулсан код | Ойлгох, сурахад зориулсан |
| **`face_recognition_system.py`** | **БҮТЭН СИСТЕМ** - Бүх функцтэй | **АЖИЛЛУУЛАХ** |

## 🚀 Бүтэн Системийг Ажиллуулах

### Арга 1: `face_recognition_system.py` шууд ажиллуулах (ЗӨВ)

```bash
# Linux/Raspberry Pi дээр
python3 face_recognition_system.py

# Windows дээр
python face_recognition_system.py

# Test mode
FACE_RECOGNITION_TEST=true python3 face_recognition_system.py
```

### Арга 2: `start.sh` ашиглах (ЗӨВ)

```bash
# Бүтэн системийг эхлүүлэх (face recognition + MagicMirror)
./start.sh

# Эсвэл test mode
./start.sh test
```

### Арга 3: `main.py` ашиглах (ЗӨВХӨН ТУРШИХ)

```bash
# Зөвхөн турших, ойлгоход зориулсан
python main.py
```

## 📋 Ялгаа

### `face_recognition_system.py` (БҮТЭН СИСТЕМ)
✅ Бүх функцтэй:
- Skin photo хадгалах
- Color correction
- Guest detection
- Sticky identity
- Image copying
- Skin analysis trigger
- Relay control (бүтэн)
- Status file update (бүтэн)
- Baseline calibration
- Distance smoothing

### `main.py` (ЗАДЛАСАН КОД)
⚠️ Зөвхөн үндсэн функцүүд:
- Зай унших
- Царай таних (хялбаршуулсан)
- Гэрэл удирдах (хялбаршуулсан)
- Статус файл (хялбаршуулсан)

## 🔧 Бүтэн Системийг Ажиллуулах

### 1. Шууд ажиллуулах:

```bash
cd D:\Diplom\MagicMirror-master
python face_recognition_system.py
```

### 2. start.sh ашиглах (Linux/Raspberry Pi):

```bash
chmod +x start.sh
./start.sh
```

### 3. npm script ашиглах:

```bash
# Test mode
npm run test-face-recognition

# Normal mode
python3 face_recognition_system.py
```

## ⚠️ Анхаарах Зүйлс

1. **`main.py` нь зөвхөн жишээ код** - бүтэн системтэй холбоогүй
2. **Бүтэн системийг ажиллуулах бол `face_recognition_system.py` ашиглах**
3. **MagicMirror-тай холбох бол `start.sh` ашиглах**

## 📊 Харьцуулалт

| Функц | face_recognition_system.py | main.py |
|-------|---------------------------|---------|
| Зай унших | ✅ Бүтэн (smoothing, baseline) | ✅ Хялбар |
| Царай таних | ✅ Бүтэн (confidence, guest) | ✅ Хялбар |
| Skin photo | ✅ Бүтэн | ❌ Байхгүй |
| Color correction | ✅ Бүтэн | ❌ Байхгүй |
| Relay control | ✅ Бүтэн (debounce) | ✅ Хялбар |
| Status file | ✅ Бүтэн (image path) | ✅ Хялбар |
| MagicMirror холбох | ✅ Бүтэн | ❌ Байхгүй |

## ✅ Зөв Ашиглах

### Бүтэн системийг ажиллуулах:
```bash
python face_recognition_system.py
```

### Зөвхөн ойлгох, турших:
```bash
python main.py
```

---

**Дүгнэлт:** `main.py` нь зөвхөн задласан код. Бүтэн системийг ажиллуулах бол **`face_recognition_system.py`** ашиглах хэрэгтэй!

