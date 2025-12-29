# 📖 Angels AI - Complete API Documentation

**Base URL:** `https://api.angels-ai.com`  
**Authentication:** Bearer Token (JWT)

---

## Authentication

### Register School
```http
POST /api/schools/register
Content-Type: application/json

{
  "school_name": "St. Mary's School",
  "country": "Uganda",
  "address": "Kampala, Uganda",
  "phone": "+256700000000",
  "email": "info@stmarys.ac.ug",
  "director_first_name": "John",
  "director_last_name": "Doe",
  "director_email": "john@stmarys.ac.ug",
  "director_phone": "+256700000001",
  "student_count_estimate": 500,
  "plan": "professional"
}
```

**Response:**
```json
{
  "success": true,
  "school_id": "uuid-here",
  "admin_email": "john@stmarys.ac.ug",
  "temporary_password": "Angels12345678",
  "login_url": "https://angels-ai.com/login?school=uuid",
  "message": "School registered successfully!"
}
```

---

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@stmarys.ac.ug",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "john@stmarys.ac.ug",
    "role": "director",
    "school_id": "uuid"
  }
}
```

---

## Universal Import

### Preview Import
```http
POST /api/import/preview
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: students.xlsx
```

**Response:**
```json
{
  "detected_columns": {
    "admission_number": "Admno",
    "first_name": "Student Name",
    "gender": "Sex"
  },
  "sample_data": [
    {
      "admission_number": "001",
      "first_name": "Peter",
      "gender": "M"
    }
  ],
  "total_rows": 500,
  "confidence_score": 0.95
}
```

### Execute Import
```http
POST /api/import/execute
Authorization: Bearer {token}
Content-Type: application/json

{
  "file_id": "temp-uuid",
  "confirmed": true
}
```

---

## Students

### List Students
```http
GET /api/students?school_id={uuid}&page=1&limit=50
Authorization: Bearer {token}
```

### Get Student
```http
GET /api/students/{student_id}
Authorization: Bearer {token}
```

### Create Student
```http
POST /api/students
Authorization: Bearer {token}
Content-Type: application/json

{
  "admission_number": "001",
  "first_name": "Peter",
  "last_name": "Mugisha",
  "gender": "M",
  "date_of_birth": "2010-05-15",
  "class_id": "uuid"
}
```

---

## Attendance

### Mark Attendance (Bulk)
```http
POST /api/attendance/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "class_id": "uuid",
  "date": "2025-12-18",
  "records": [
    {"student_id": "uuid1", "status": "present"},
    {"student_id": "uuid2", "status": "absent"}
  ]
}
```

---

## WhatsApp

### Send Message
```http
POST /api/whatsapp/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "to": "+256700000000",
  "message": "Your fees are due. Please pay UGX 500,000 by Dec 25."
}
```

### Webhook (Incoming Messages)
```http
POST /api/whatsapp/webhook
Content-Type: application/json

{
  "From": "whatsapp:+256700000000",
  "Body": "What are the school fees?"
}
```

---

## 24/7 Receptionist

### Chat
```http
POST /api/receptionist/chat
Content-Type: application/json

{
  "message": "What are your school fees?",
  "school_id": "uuid",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "reply": "Our school fees vary by grade level. Please contact...",
  "suggestions": ["View fee structure", "Contact admissions"],
  "session_id": "uuid"
}
```

---

## Branding

### Get School Branding
```http
GET /api/branding/{school_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "school_id": "uuid",
  "brand_name": "St. Mary's School",
  "primary_color": "#1a4d2e",
  "secondary_color": "#2d6a4f",
  "logo_url": "https://cdn.../logo.png",
  "tagline": "Excellence in Education"
}
```

### Update Branding
```http
PUT /api/branding/{school_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "primary_color": "#0000ff",
  "logo_url": "https://new-logo.png"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Rate Limiting

- **Default:** 1000 requests/hour per user
- **Webhooks:** No limit
- **Public endpoints:** 100 requests/hour per IP

**Headers:**
- `X-RateLimit-Limit` - Max requests
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

---

## Webhooks

### USSD Webhook
```http
POST /api/ussd/webhook
Content-Type: application/json

{
  "sessionId": "session-id",
  "phoneNumber": "+256700000000",
  "text": "1*2"
}
```

---

## Testing

**Sandbox Base URL:** `https://sandbox-api.angels-ai.com`

**Test Credentials:**
```
Email: test@angels-ai.com
Password: TestPass123
School ID: demo-school-001
```

---

*For more details, see [Interactive API Explorer](https://api.angels-ai.com/docs)*
