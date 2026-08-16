from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_security_flow():
    # 1. Test Registration
    reg_response = client.post(
        "/register",
        json={"username": "ci_cd_tester", "password": "securepassword123"}
    )
    # Allow 400 in case the test user already exists in the database
    assert reg_response.status_code in [201, 400] 

    # 2. Test Login & Get Cookie
    login_response = client.post(
        "/login",
        data={"username": "ci_cd_tester", "password": "securepassword123"}
    )
    assert login_response.status_code == 200
    
    # Verify the HTTP-Only cookie was actually created
    cookie = login_response.cookies.get("access_token")
    assert cookie is not None

    # 3. Test Injecting Data (Without Cookie - Should Fail)
    client.cookies.clear()
    blocked_response = client.post(
        "/records",
        json={"status": "processed", "metric": 50.0}
    )
    assert blocked_response.status_code == 401 # 401 Unauthorized

    # 4. Test Injecting Data (With Cookie - Should Succeed)
    success_response = client.post(
        "/records",
        json={"status": "processed", "metric": 50.0},
        cookies={"access_token": cookie} # <-- Simulates the browser sending the cookie back
    )
    assert success_response.status_code == 201