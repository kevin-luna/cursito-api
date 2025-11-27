# PDF Reports Guide

This guide explains how to use the PDF report generation endpoints in the Cursito API.

## Overview

The API provides five PDF report endpoints that generate professional, formatted documents for various purposes:

1. **Attendance List** - Course attendance with student details and grades
2. **Enrollment Certificate** - Individual enrollment documentation
3. **Instructor Courses List** - All courses taught by an instructor
4. **Follow-up Survey Responses** - Survey answers for CSAT evaluation
5. **Opinion Survey Responses** - Survey answers for opinion evaluation

## Technology

Reports are generated using **ReportLab**, a powerful Python PDF library that creates professional documents with:
- Custom styling and formatting
- Tables with alternating row colors
- Headers and footers
- Proper page layout and margins

## Endpoints

### 1. Attendance List

**Endpoint:** `GET /reports/attendance/{course_id}`

**Description:** Generates a PDF with the attendance list for a course, including:
- Course information (name, type, modality, dates, schedule)
- List of enrolled workers with:
  - Sequential number
  - Full name
  - RFC
  - Gender (M/F)
  - Final grade
- Total participant count
- Generation timestamp

**Example:**
```bash
curl -O "http://localhost:8000/reports/attendance/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

**Response:** PDF file downloaded as `attendance_list_{course_id}.pdf`

---

### 2. Enrollment Certificate

**Endpoint:** `GET /reports/enrollment/{worker_id}/{course_id}`

**Description:** Generates a PDF certificate documenting a worker's enrollment in a course, including:

**Worker Information:**
- Full name
- RFC
- CURP
- Email
- Phone
- Gender
- Department
- Role

**Course Information:**
- Course name
- Objective
- Type (Diplomado/Taller)
- Modality (Virtual/Presencial)
- Profile (Formación/Actualización Docente)
- Start and end dates
- Schedule
- Goals

**Enrollment Information:**
- Enrollment date
- Final grade (if available)

**Example:**
```bash
curl -O "http://localhost:8000/reports/enrollment/worker-uuid/course-uuid"
```

**Response:** PDF file downloaded as `enrollment_certificate_{worker_id}_{course_id}.pdf`

---

### 3. Instructor Courses List

**Endpoint:** `GET /reports/instructor-courses/{worker_id}`

**Description:** Generates a PDF listing all courses taught by an instructor, including:

**Instructor Information:**
- Full name
- RFC
- Department

**For Each Course:**
- Course name
- Objective
- Type
- Modality
- Profile
- Dates
- Schedule
- Goals
- Details

**Example:**
```bash
curl -O "http://localhost:8000/reports/instructor-courses/instructor-worker-uuid"
```

**Response:** PDF file downloaded as `instructor_courses_{worker_id}.pdf`

---

### 4. Follow-up Survey Responses

**Endpoint:** `GET /reports/survey/{worker_id}/{course_id}/followup`

**Description:** Generates a PDF with a worker's responses to the follow-up (CSAT) survey for a specific course in form format.

**Format:** Survey presented in form style showing:
- Questions grouped by sections (Aplicación de Conocimientos, Beneficios del Curso, Obstáculos, Comentarios)
- Likert scale questions with all 5 options displayed, selected option marked with ✓ and in bold
- Multiple selection questions (checkboxes) with selected items marked with ✓ and in bold
- Non-selected options marked with ○
- Text responses displayed in full
- **No tables used** - all content presented as formatted paragraphs and lists

**Includes:**
- Worker and course information
- Section 1: Knowledge Application (3 Likert scale questions)
- Section 2: Course Benefits (8 multiple-choice options)
- Section 3: Obstacles (3 checkbox options + optional text)
- Section 4: Comments and Suggestions (text response)

**Survey ID:** `3d1fa6a2-6d4a-42fa-a474-68c83156f541`

**Example:**
```bash
curl -O "http://localhost:8000/reports/survey/worker-uuid/course-uuid/followup"
```

**Response:** PDF file downloaded as `followup_survey_{worker_id}_{course_id}.pdf`

---

### 5. Opinion Survey Responses

**Endpoint:** `GET /reports/survey/{worker_id}/{course_id}/opinion`

**Description:** Generates a PDF with a worker's responses to the opinion survey for a specific course in form format.

**Format:** Survey presented in form style showing:
- Questions grouped by sections (Instructor, Material Didáctico, Curso, Infraestructura, Comentarios)
- Each Likert scale question with all 5 options displayed, selected option marked with ✓ and in bold
- Non-selected options marked with ○
- Text responses displayed in full
- **No tables used** - all content presented as formatted paragraphs

**Includes:**
- Worker and course information
- Section 1: Instructor (7 Likert scale questions)
- Section 2: Educational Material (3 Likert scale questions)
- Section 3: Course (4 Likert scale questions)
- Section 4: Infrastructure (6 Likert scale questions)
- Section 5: Comments and Suggestions (text response)

**Survey ID:** `c2a77b75-8552-4fe0-ab49-231803244ace`

**Example:**
```bash
curl -O "http://localhost:8000/reports/survey/worker-uuid/course-uuid/opinion"
```

**Response:** PDF file downloaded as `opinion_survey_{worker_id}_{course_id}.pdf`

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK** - PDF generated successfully
- **404 Not Found** - Resource not found (worker, course, enrollment, or survey answers)
- **500 Internal Server Error** - Error during PDF generation

**Error Response Format:**
```json
{
  "detail": "Error message describing the issue"
}
```

## Testing

A test script is provided at `test_reports.py` to verify all endpoints:

```bash
# Start the API server first
python main.py

# In another terminal, run the test script
python test_reports.py
```

**Note:** Update the UUIDs in `test_reports.py` with actual IDs from your database.

## Frontend Integration

### Using Axios (Vue/React):

```javascript
async function downloadAttendanceList(courseId) {
  const response = await axios.get(
    `/reports/attendance/${courseId}`,
    { responseType: 'blob' }
  )

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `attendance_${courseId}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
}
```

### Using Fetch API:

```javascript
async function downloadReport(url, filename) {
  const response = await fetch(url)
  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = downloadUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
}

// Usage
downloadReport(
  `/reports/enrollment/${workerId}/${courseId}`,
  'enrollment.pdf'
)
```

## PDF Styling

All PDFs include:
- **Professional header** with title in primary blue color
- **Structured sections** with clear headings
- **Tables** with:
  - Blue header background
  - Alternating row colors (white/light gray)
  - Grid borders
  - Proper padding and alignment
- **Footer** with generation timestamp
- **Proper margins** and page layout

## Customization

To modify PDF styling, edit `src/services/pdf_report_service.py`:

- **Colors:** Update `colors.HexColor()` values in table styles
- **Fonts:** Modify `FONTNAME` in TableStyle
- **Layout:** Adjust `colWidths`, `topMargin`, `bottomMargin` in SimpleDocTemplate
- **Styles:** Customize ParagraphStyle in `_get_styles()` method

## Dependencies

The PDF generation feature requires:
- `reportlab` - PDF generation library
- `pillow` - Image processing (reportlab dependency)

These are automatically installed with:
```bash
pip install -r requirements.txt
```

## Performance Considerations

- PDF generation is synchronous and may take 1-3 seconds for large datasets
- For courses with 100+ enrollments, consider implementing caching
- PDFs are generated in-memory using BytesIO for efficient streaming
- No temporary files are created on disk

## Troubleshooting

### "Course not found" error
- Verify the course UUID exists in the database
- Check that you're using the correct UUID format

### "No answers found for this survey" error
- Ensure the worker has completed the survey for that course
- Verify the survey_id matches the expected survey type

### "Enrollment not found" error
- Confirm the worker is enrolled in the specified course
- Check that the enrollment record exists in the database

### PDF rendering issues
- Ensure reportlab is properly installed
- Check for special characters in text fields that may cause encoding issues
- Verify all referenced data exists (workers, courses, departments, etc.)
