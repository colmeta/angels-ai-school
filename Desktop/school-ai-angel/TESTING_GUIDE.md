# 🧪 COMPREHENSIVE TESTING GUIDE

## ✅ DEPLOYMENT STATUS

**GitHub**: ✅ Pushed successfully
- Repository: https://github.com/colmeta/angels-ai-school
- Commit: `1a6eae0`

**Render**: ⏳ Deploying...
- Check status: https://dashboard.render.com/

**Vercel**: ⏳ Pending
- Deploy: https://vercel.com/new

---

## 📋 TESTING CHECKLIST

### 1. BACKEND HEALTH CHECK

**When Render finishes deploying:**

```bash
# Replace with your Render URL
curl https://your-app.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-24T10:52:00Z",
  "memory_mb": 285,
  "memory_percent": 55.7,
  "version": "1.0.0"
}
```

**✅ Pass Criteria:**
- Status code: 200
- Memory < 400MB
- Response time < 3s

---

### 2. MEMORY OPTIMIZATION TEST (512MB Render)

**Test Memory Usage:**

```bash
# Check memory header
curl -I https://your-app.onrender.com/api/health
```

Look for header: `X-Memory-Usage-MB: 285`

**Load Test (10 requests):**
```bash
for i in {1..10}; do
  curl https://your-app.onrender.com/api/health &
done
wait
```

**✅ Pass Criteria:**
- Memory stays < 400MB
- No "Out of Memory" errors
- All requests return 200

---

### 3. THREE-TIER AI SYSTEM TEST

#### Test Core Mode (Offline)
1. Open browser DevTools
2. Go to Application → Local Storage
3. Set: `ai_mode = "core"`
4. Refresh page
5. Check that AI loads fully offline models

**✅ Pass Criteria:**
- Models load without internet
- ~200MB app size
- No cloud requests

#### Test Hybrid Mode (Recommended)
1. Set: `ai_mode = "hybrid"`
2. Refresh page
3. Upload a photo
4. Verify sync to R2

**✅ Pass Criteria:**
- Quantized models load
- ~50MB app size
- Cloud sync works
- Works offline first

#### Test Flash Mode (Cloud)
1. Set: `ai_mode = "flash"`
2. Refresh page
3. Check Network tab

**✅ Pass Criteria:**
- Minimal local models
- ~30MB app size
- Cloud API used

---

### 4. MULTI-LANGUAGE TEST

**Test Language Switcher:**

1. Open app
2. Click language dropdown (Globe icon)
3. Switch to **Luganda** (🇺🇬)
   - Verify UI text changes
   - Check "Get Started" → "Tandika Bwereere"
4. Switch to **Swahili** (🇹🇿)
   - Check "Features" → "Vipengele"
5. Switch back to **English** (🇬🇧)

**✅ Pass Criteria:**
- All 3 languages work
- No missing translations
- Language persists on refresh

---

### 5. PHOTO UPLOAD TEST

**Test Photo Processing:**

```bash
# Using curl
curl -X POST https://your-app.onrender.com/api/documents/photos/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-photo.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Or via UI:**
1. Login to app
2. Go to Students → New Student
3. Click "Upload Photo"
4. Select a photo (2MB max)
5. Verify:
   - Photo auto-crops to passport size
   - Thumbnail generated
   - Preview shows correctly

**✅ Pass Criteria:**
- Upload completes < 3 seconds
- Photo resized to 300x400
- Thumbnail 100x100
- Base64 returned
- No memory errors

---

### 6. STUDENT ID CARD TEST

**Generate ID Card:**

```bash
curl -X POST https://your-app.onrender.com/api/documents/id-cards/student \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_name": "John Doe",
    "student_id": "STU001",
    "class_name": "Grade 5A",
    "school_name": "Test School",
    "photo_base64": "..."
  }' \
  --output student_id.png
```

**Verify:**
1. Download generated `student_id.png`
2. Check resolution: 1011x638 pixels
3. Check DPI: 300 (print quality)
4. Verify photo appears correctly
5. Check all fields rendered

**✅ Pass Criteria:**
- File size: ~200KB
- High quality (no pixelation)
- Photo centered
- Text readable
- Printable quality

---

### 7. PASS-OUT SLIP TEST

**Generate Pass-Out:**

```bash
curl -X POST https://your-app.onrender.com/api/documents/pass-out-slips/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_name": "Jane Smith",
    "student_id": "STU002",
    "class_name": "Grade 4B",
    "reason": "Medical appointment",
    "departure_time": "10:00 AM",
    "expected_return": "2:00 PM",
    "authorized_by": "Mr. Principal",
    "school_name": "Test School",
    "parent_phone": "+256700000000"
  }' \
  --output pass_out.png
```

**Verify:**
1. Download `pass_out.png`
2. Check size: A5 (1754x1240)
3. Check DPI: 300
4. Verify all fields present
5. Check reference number generated

**✅ Pass Criteria:**
- Professional layout
- All info visible
- Signature lines present
- Warning notice shown
- Reference number unique

---

### 8. REPORT CARD TEST

**Generate Report Card:**

```bash
curl -X POST https://your-app.onrender.com/api/documents/report-cards/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_name": "Alice Johnson",
    "student_id": "STU003",
    "class_name": "Grade 6C",
    "term": "First",
    "year": "2024",
    "subjects": [
      {"name": "Mathematics", "score": 85, "grade": "A", "remarks": "Excellent"},
      {"name": "English", "score": 78, "grade": "B+", "remarks": "Good"},
      {"name": "Science", "score": 92, "grade": "A+", "remarks": "Outstanding"}
    ],
    "school_name": "Test School",
    "school_address": "123 Test St, Kampala",
    "class_teacher": "Mrs. Teacher"
  }' \
  --output report_card.png
```

**Verify:**
1. Download `report_card.png`
2. Check size: A4 (2480x3508)
3. Check DPI: 300 (print quality)
4. Verify student photo appears
5. Check grade colors (A=green, F=red)
6. Verify average calculated correctly

**✅ Pass Criteria:**
- Professional A4 layout
- Student photo visible
- All subjects listed
- Grades color-coded
- Average calculated
- Signature sections present
- High-quality printing

---

### 9. BATCH ID GENERATION TEST

**Generate 10 IDs at once:**

```bash
curl -X POST https://your-app.onrender.com/api/documents/id-cards/batch/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "students": [
      {"student_name": "Student 1", "student_id": "S001", "class_name": "G5A", "school_name": "Test"},
      {"student_name": "Student 2", "student_id": "S002", "class_name": "G5A", "school_name": "Test"},
      ... (add 8 more)
    ]
  }'
```

**✅ Pass Criteria:**
- All 10 IDs generated
- Processing time < 30 seconds
- Memory stays < 400MB
- No failures

---

### 10. LANDING PAGE TEST

**Open:** `https://your-vercel-app.vercel.app`

**Verify:**
1. ✅ Hero section loads
2. ✅ Animated gradients work
3. ✅ "100% Free Forever" badge visible
4. ✅ Three-tier cards (Core/Hybrid/Flash)
5. ✅ Features grid displays
6. ✅ CTA buttons work
7. ✅ Language switcher present
8. ✅ Mobile responsive
9. ✅ No pricing tiers shown
10. ✅ Links to signup work

**Performance:**
- Lighthouse score > 90
- First Contentful Paint < 2s
- Time to Interactive < 3s

---

### 11. AI SETTINGS PANEL TEST

**Navigate to Settings:**

1. Login
2. Go to Settings → AI Configuration
3. Verify:
   - Device RAM detected
   - Current mode shown
   - Recommended mode highlighted
   - Mode descriptions accurate
4. Switch modes:
   - Core → Hybrid → Flash
   - Verify page reloads
   - Check mode persists

**✅ Pass Criteria:**
- RAM detection works
- Mode switching smooth
- Compatibility warnings show
- Current config displayed

---

### 12. A/B TESTING VERIFICATION

**Check Experiments Running:**

```bash
curl https://your-app.onrender.com/api/experiments \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:**
```json
{
  "experiments": [
    {"name": "ai_mode_comparison", "status": "active"},
    {"name": "ai_speed_vs_accuracy", "status": "active"},
    {"name": "cloud_sync_adoption", "status": "active"},
    {"name": "quantized_model_satisfaction", "status": "active"}
  ]
}
```

**✅ Pass Criteria:**
- 4 experiments active
- Users randomly assigned
- Tracking works

---

## 🎯 FINAL INTEGRATION TEST

**Complete User Flow:**

1. **Visit Landing Page**
   - Switch language to Luganda
   - Click "Tandika Bwereere"

2. **Sign Up**
   - Use Google OAuth
   - Verify 100% free signup
   - No pricing options shown

3. **Add Student**
   - Upload photo
   - Fill details
   - Save

4. **Generate ID Card**
   - Select student
   - Click "Generate ID"
   - Download PNG
   - Print test (check 300 DPI quality)

5. **Create Pass-Out Slip**
   - Select student
   - Fill reason/time
   - Generate
   - Download
   - Print test

6. **Generate Report Card**
   - Add grades
   - Include photo
   - Generate
   - Download
   - Print test (A4, high quality)

7. **Monitor Memory**
   - Check Render dashboard
   - Verify < 400MB throughout

---

## 📊 SUCCESS METRICS

**Must Pass:**
- [ ] Backend deploys successfully
- [ ] Memory stays < 400MB
- [ ] All APIs return 200
- [ ] Photos upload < 3s
- [ ] IDs generate < 5s
- [ ] Report cards < 10s
- [ ] Batch 10 IDs < 30s
- [ ] All 3 AI modes work
- [ ] All 3 languages work
- [ ] Landing page loads < 2s
- [ ] No console errors
- [ ] Print quality is 300 DPI

**Performance:**
- Response times < 5s
- Uptime > 99%
- No crashes
- No memory leaks

---

## 🐛 IF TESTS FAIL

### Out of Memory
- Check Render logs
- Verify single worker config
- Check photo size limits
- Force garbage collection

### Slow Responses
- Check worker count (should be 1)
- Verify image optimization
- Check R2 connection

### Photo Upload Fails
- Check file size < 2MB
- Verify R2 credentials
- Check permissions

### ID Card Blank
- Verify Pillow installed
- Check font files
- Test image generation locally

---

## 📝 TESTING REPORT TEMPLATE

```markdown
# Test Report - [Date]

## Deployment
- Backend URL: 
- Frontend URL:
- Commit: 1a6eae0

## Results

### Backend Health
- Status: ✅/❌
- Memory: XXX MB
- Response Time: XX ms

### AI Modes
- Core: ✅/❌
- Hybrid: ✅/❌
- Flash: ✅/❌

### Multi-Language
- English: ✅/❌
- Luganda: ✅/❌
- Swahili: ✅/❌

### Photo Features
- Upload: ✅/❌ (XX seconds)
- ID Cards: ✅/❌ (XX seconds)
- Pass-Out: ✅/❌ (XX seconds)
- Report Cards: ✅/❌ (XX seconds)

### Print Quality
- ID Card DPI: XXX ✅/❌
- Report Card DPI: XXX ✅/❌

### Overall: ✅ PASS / ❌ FAIL

## Issues Found
1. [Issue description]

## Recommendations
1. [Recommendation]
```

---

**Ready to test once Render deploys! 🚀**

I'll walk you through each test step-by-step when deployment completes.
