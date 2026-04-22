"""
Security Fixes Verification Test
Tests all critical security fixes for GhostOffice v3.1.0
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Dashboard.auth import (
    init_auth_db,
    create_session_token,
    verify_session_token,
    validate_password_strength,
    change_password,
    force_password_change_required,
    get_db_connection
)


def test_jwt_secret_no_fallback():
    """Test 1: JWT secret has no fallback"""
    print("\n" + "="*60)
    print("TEST 1: JWT Secret No Fallback")
    print("="*60)
    
    # Save original JWT_SECRET
    original_secret = os.getenv("JWT_SECRET")
    
    try:
        # Test 1: Missing JWT_SECRET should raise error
        os.environ.pop("JWT_SECRET", None)
        
        try:
            create_session_token(user_id=1)
            print("❌ FAIL: Should have raised ValueError for missing JWT_SECRET")
            return False
        except ValueError as e:
            if "JWT_SECRET environment variable must be set" in str(e):
                print("✅ PASS: Correctly raises ValueError when JWT_SECRET is missing")
            else:
                print(f"❌ FAIL: Wrong error message: {e}")
                return False
        
        # Test 2: Valid JWT_SECRET should work
        os.environ["JWT_SECRET"] = "test-secret-key-for-testing"
        
        # Initialize test database
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["DATA_DIR"] = tmpdir
            init_auth_db()
            
            try:
                token = create_session_token(user_id=1)
                if token:
                    print("✅ PASS: Token created successfully with valid JWT_SECRET")
                    
                    # Test 3: Verify token works
                    payload = verify_session_token(token)
                    if payload and payload.get("user_id") == 1:
                        print("✅ PASS: Token verified successfully")
                    else:
                        print("❌ FAIL: Token verification failed")
                        return False
                else:
                    print("❌ FAIL: Failed to create token with valid JWT_SECRET")
                    return False
            except Exception as e:
                print(f"❌ FAIL: Error with valid JWT_SECRET: {e}")
                return False
        
        print("✅ TEST 1 PASSED: JWT secret has no fallback")
        return True
        
    finally:
        # Restore original JWT_SECRET
        if original_secret:
            os.environ["JWT_SECRET"] = original_secret
        else:
            os.environ.pop("JWT_SECRET", None)


def test_admin_password_change():
    """Test 2: Admin password change enforcement"""
    print("\n" + "="*60)
    print("TEST 2: Admin Password Change Enforcement")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["DATA_DIR"] = tmpdir
        os.environ["JWT_SECRET"] = "test-secret-key"
        
        # Initialize fresh database
        init_auth_db()
        
        # Check admin user was created with requires_password_change = True
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        conn.close()
        
        if not admin:
            print("❌ FAIL: Admin user not created")
            return False
        
        # Convert Row to dict for easier access
        admin_dict = dict(admin)
        
        if admin_dict.get("requires_password_change"):
            print("✅ PASS: Admin user created with requires_password_change = True")
        else:
            print("❌ FAIL: Admin user should require password change")
            return False
        
        # Test password strength validation
        test_cases = [
            ("short", False, "too short"),
            ("longbutuppercase", False, "no special chars"),
            ("LongButNoDigits!", False, "no digits"),
            ("NOLOWERCASE123!", False, "no lowercase"),
            ("nouppercase123!", False, "no uppercase"),
            ("ValidPass123!", True, "valid password"),
        ]
        
        for password, should_pass, description in test_cases:
            is_valid, message = validate_password_strength(password)
            if is_valid == should_pass:
                print(f"✅ PASS: Password '{description}' validation correct")
            else:
                print(f"❌ FAIL: Password '{description}' validation failed: {message}")
                return False
        
        # Test password change functionality
        admin_id = admin["id"]
        
        # First, get the temporary password from the database (we'd need to capture this from stdout in real usage)
        # For testing, we'll directly test the change_password function
        
        # Test changing password with wrong old password
        success, message = change_password(admin_id, "wrong_old_pass", "NewValidPass123!")
        if not success:
            print("✅ PASS: Correctly rejects wrong old password")
        else:
            print("❌ FAIL: Should reject wrong old password")
            return False
        
        # Test changing password with weak new password
        success, message = change_password(admin_id, "admin", "weak")
        if not success:
            print("✅ PASS: Correctly rejects weak new password")
        else:
            print("❌ FAIL: Should reject weak new password")
            return False
        
        # Test force password change required
        if force_password_change_required(admin_id):
            print("✅ PASS: force_password_change_required returns True for new admin")
        else:
            print("❌ FAIL: force_password_change_required should return True")
            return False
        
        print("✅ TEST 2 PASSED: Admin password change enforcement works")
        return True


def test_csrf_protection():
    """Test 3: CSRF protection is configured"""
    print("\n" + "="*60)
    print("TEST 3: CSRF Protection Configuration")
    print("="*60)
    
    # Check if Flask-WTF is available
    try:
        from flask_wtf.csrf import CSRFProtect
        print("✅ PASS: Flask-WTF is available")
    except ImportError:
        print("❌ FAIL: Flask-WTF not installed")
        return False
    
    # Check if CSRF is configured in app.py
    app_py_path = Path(__file__).parent.parent / "Dashboard" / "app.py"
    if not app_py_path.exists():
        print("❌ FAIL: app.py not found")
        return False
    
    app_content = app_py_path.read_text()
    
    if "CSRFProtect" in app_content:
        print("✅ PASS: CSRFProtect is imported in app.py")
    else:
        print("❌ FAIL: CSRFProtect not imported in app.py")
        return False
    
    if "csrf = CSRFProtect(app)" in app_content:
        print("✅ PASS: CSRF protection is initialized")
    else:
        print("❌ FAIL: CSRF protection not initialized")
        return False
    
    # Check if login form has CSRF token
    login_template_path = Path(__file__).parent.parent / "Dashboard" / "templates" / "login.html"
    if login_template_path.exists():
        login_content = login_template_path.read_text()
        if 'csrf_token()' in login_content:
            print("✅ PASS: Login form includes CSRF token")
        else:
            print("❌ FAIL: Login form missing CSRF token")
            return False
    else:
        print("❌ FAIL: login.html template not found")
        return False
    
    # Check if settings form has CSRF token
    settings_template_path = Path(__file__).parent.parent / "Dashboard" / "templates" / "settings.html"
    if settings_template_path.exists():
        settings_content = settings_template_path.read_text()
        if 'csrf_token()' in settings_content:
            print("✅ PASS: Settings form includes CSRF token")
        else:
            print("❌ FAIL: Settings form missing CSRF token")
            return False
    else:
        print("❌ FAIL: settings.html template not found")
        return False
    
    print("✅ TEST 3 PASSED: CSRF protection is properly configured")
    return True


def test_env_file_updates():
    """Test 4: .env.example and documentation updates"""
    print("\n" + "="*60)
    print("TEST 4: Environment File and Documentation Updates")
    print("="*60)
    
    # Check .env.example has JWT_SECRET
    env_example_path = Path(__file__).parent.parent / ".env.example"
    if not env_example_path.exists():
        print("❌ FAIL: .env.example not found")
        return False
    
    env_content = env_example_path.read_text()
    
    if "JWT_SECRET" in env_content:
        print("✅ PASS: .env.example includes JWT_SECRET")
    else:
        print("❌ FAIL: .env.example missing JWT_SECRET")
        return False
    
    if "FLASK_SECRET_KEY" in env_content:
        print("✅ PASS: .env.example includes FLASK_SECRET_KEY")
    else:
        print("❌ FAIL: .env.example missing FLASK_SECRET_KEY")
        return False
    
    # Check README has security documentation
    readme_path = Path(__file__).parent.parent / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text()
        if "JWT_SECRET" in readme_content or "security" in readme_content.lower():
            print("✅ PASS: README includes security documentation")
        else:
            print("⚠️  WARNING: README may need security documentation")
    else:
        print("⚠️  WARNING: README.md not found")
    
    print("✅ TEST 4 PASSED: Environment files properly updated")
    return True


def test_database_schema():
    """Test 5: Database schema includes security columns"""
    print("\n" + "="*60)
    print("TEST 5: Database Schema Security Columns")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["DATA_DIR"] = tmpdir
        os.environ["JWT_SECRET"] = "test-secret-key"
        
        # Initialize database
        init_auth_db()
        
        # Check users table schema
        db_path = Path(tmpdir) / "dashboard.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Users table columns: {columns}")
        
        if "requires_password_change" in columns:
            print("✅ PASS: users table has requires_password_change column")
        else:
            print("❌ FAIL: users table missing requires_password_change column")
            print(f"Available columns: {columns}")
            conn.close()
            return False
        
        # Check sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        if cursor.fetchone():
            print("✅ PASS: sessions table exists")
        else:
            print("❌ FAIL: sessions table missing")
            conn.close()
            return False
        
        # Verify admin user was created with requires_password_change = True
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            # Get column index for requires_password_change
            col_index = columns.index("requires_password_change")
            requires_change = admin[col_index]
            if requires_change:
                print("✅ PASS: Admin user has requires_password_change = True")
            else:
                print("❌ FAIL: Admin user should have requires_password_change = True")
                conn.close()
                return False
        else:
            print("❌ FAIL: Admin user not found")
            conn.close()
            return False
        
        conn.close()
        print("✅ TEST 5 PASSED: Database schema includes security columns")
        return True


def run_all_tests():
    """Run all security tests"""
    print("\n" + "="*60)
    print("🔐 GHOSTOFFICE SECURITY FIXES VERIFICATION")
    print("="*60)
    
    tests = [
        ("JWT Secret No Fallback", test_jwt_secret_no_fallback),
        ("Admin Password Change", test_admin_password_change),
        ("CSRF Protection", test_csrf_protection),
        ("Environment File Updates", test_env_file_updates),
        ("Database Schema", test_database_schema),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SECURITY TESTS PASSED!")
        print("✅ GhostOffice v3.1.0 is ready for production deployment")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix before deployment.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)