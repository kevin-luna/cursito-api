"""
Simple test script to verify PDF report endpoints
Run this after starting the API server
"""
import requests
from uuid import UUID

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_attendance_list(course_id: str):
    """Test attendance list PDF generation"""
    print(f"\n📋 Testing attendance list for course: {course_id}")
    response = requests.get(f"{BASE_URL}/reports/attendance/{course_id}")

    if response.status_code == 200:
        filename = f"test_attendance_{course_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as: {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

def test_enrollment_certificate(worker_id: str, course_id: str):
    """Test enrollment certificate PDF generation"""
    print(f"\n📜 Testing enrollment certificate for worker: {worker_id}, course: {course_id}")
    response = requests.get(f"{BASE_URL}/reports/enrollment/{worker_id}/{course_id}")

    if response.status_code == 200:
        filename = f"test_enrollment_{worker_id}_{course_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as: {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

def test_instructor_courses_list(worker_id: str):
    """Test instructor courses list PDF generation"""
    print(f"\n👨‍🏫 Testing instructor courses list for worker: {worker_id}")
    response = requests.get(f"{BASE_URL}/reports/instructor-courses/{worker_id}")

    if response.status_code == 200:
        filename = f"test_instructor_courses_{worker_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as: {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

def test_followup_survey(worker_id: str, course_id: str):
    """Test follow-up survey responses PDF generation"""
    print(f"\n📊 Testing follow-up survey for worker: {worker_id}, course: {course_id}")
    response = requests.get(f"{BASE_URL}/reports/survey/{worker_id}/{course_id}/followup")

    if response.status_code == 200:
        filename = f"test_followup_survey_{worker_id}_{course_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as: {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

def test_opinion_survey(worker_id: str, course_id: str):
    """Test opinion survey responses PDF generation"""
    print(f"\n💭 Testing opinion survey for worker: {worker_id}, course: {course_id}")
    response = requests.get(f"{BASE_URL}/reports/survey/{worker_id}/{course_id}/opinion")

    if response.status_code == 200:
        filename = f"test_opinion_survey_{worker_id}_{course_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Success! PDF saved as: {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    print("🚀 Starting PDF Report Endpoint Tests")
    print("=" * 60)
    print("\n⚠️  Note: Replace the UUIDs below with actual IDs from your database")
    print("=" * 60)

    # Example UUIDs - replace with actual IDs from your database
    EXAMPLE_COURSE_ID = "00000000-0000-0000-0000-000000000001"
    EXAMPLE_WORKER_ID = "00000000-0000-0000-0000-000000000001"

    print("\n🔍 Testing all report endpoints...")

    # Test all endpoints
    test_attendance_list(EXAMPLE_COURSE_ID)
    test_enrollment_certificate(EXAMPLE_WORKER_ID, EXAMPLE_COURSE_ID)
    test_instructor_courses_list(EXAMPLE_WORKER_ID)
    test_followup_survey(EXAMPLE_WORKER_ID, EXAMPLE_COURSE_ID)
    test_opinion_survey(EXAMPLE_WORKER_ID, EXAMPLE_COURSE_ID)

    print("\n" + "=" * 60)
    print("✨ Testing complete!")
    print("=" * 60)
