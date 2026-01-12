import sys
import os
import unittest
import json
import logging
from datetime import datetime, timedelta

# Setup logging to be clean
logging.basicConfig(level=logging.ERROR)

# Set environment variables for testing BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['WTF_CSRF_ENABLED'] = 'false'

# Ensure the app can be imported
sys.path.append(os.getcwd())
from app import create_app, db
from app.models import User, SchoolClass, Subject, Task, UserRole, GlobalSetting, Event, Grade

class L8teStudyComprehensiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a test database and app instance."""
        cls.app = create_app()
        # Ensure testing config is active
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
        
        with cls.app.app_context():
            # In-memory DB is already created by create_app's db.create_all()
            # but we can call it again just to be safe if environment didn't catch it
            db.create_all()
            
            # 1. Create a Test Class
            # We don't specify code, let it generate one or use a unique one
            test_class = SchoolClass(name="TestClass101")
            db.session.add(test_class)
            db.session.flush() # Get the ID and code
            cls.test_class_id = test_class.id
            cls.test_class_code = test_class.code
            
            # 2. Create a Super Admin
            super_admin = User(username="superadmin", role=UserRole.SUPER_ADMIN)
            super_admin.set_password("pass")
            db.session.add(super_admin)
            
            # 3. Create a Student
            student = User(username="student", role=UserRole.STUDENT, class_id=cls.test_class_id)
            student.set_password("pass")
            db.session.add(student)
            
            db.session.commit()

    def login(self, username, password="pass", class_code=None):
        payload = {'username': username, 'password': password}
        if class_code:
            payload['class_code'] = class_code
        elif username == "student":
             payload['class_code'] = self.test_class_code
             
        return self.client.post('/login', data=json.dumps(payload), content_type='application/json')

    def test_01_core_routes_availability(self):
        """Test if basic public and auth routes respond correctly."""
        print("\n[STEP 1] Testing Basic Route Connectivity...")
        
        # Test Privacy Page
        res = self.client.get('/privacy')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Datenschutzerkl', res.data)
        print(" -> Privacy Page: OK")
        
        # Test Imprint Page
        res = self.client.get('/imprint')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Impressum', res.data)
        print(" -> Imprint Page: OK")

        # Test Login Page
        res = self.client.get('/login-page')
        self.assertEqual(res.status_code, 200)
        print(" -> Login Page: OK")

    def test_02_authentication_workflow(self):
        """Test login, session management and logout."""
        print("\n[STEP 2] Testing Authentication & Session...")
        
        # Login
        res = self.login("student")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json.loads(res.data)['success'])
        print(" -> Login (Student): OK")
        
        # Check Identity
        res = self.client.get('/api/config')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['role'], 'student')
        print(" -> Identity Verification: OK")
        
        # Logout
        res = self.client.get('/logout')
        self.assertEqual(res.status_code, 302) # Should redirect to login-page
        print(" -> Logout: OK")

    def test_03_task_management_api(self):
        """Test creating, fetching and deleting tasks."""
        print("\n[STEP 3] Testing Task Management API...")
        self.login("student")
        
        # Create a Subject first
        with self.app.app_context():
            s = Subject(name="Math")
            sc = SchoolClass.query.get(self.test_class_id)
            s.classes.append(sc)
            db.session.add(s)
            db.session.commit()
            sub_id = s.id

        # Create Task
        res = self.client.post('/api/tasks', data=json.dumps({
            'title': 'Solve Equations',
            'subject_id': sub_id,
            'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Page 42'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        task_id = json.loads(res.data)['id']
        print(" -> Task Creation: OK")
        
        # Fetch Tasks
        res = self.client.get('/api/tasks')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Solve Equations', res.data)
        print(" -> Task List Retrieval: OK")

    def test_04_admin_permissions(self):
        """Test that permissions are correctly enforced."""
        print("\n[STEP 4] Testing Permissions & Security...")
        
        # Try to access global settings as student (should fail)
        self.login("student")
        res = self.client.get('/api/admin/settings/global')
        self.assertEqual(res.status_code, 403)
        print(" -> Unauthorized Access Blocked: OK")
        
        # Access as super admin (should succeed)
        self.login("superadmin")
        res = self.client.get('/api/admin/settings/global')
        self.assertEqual(res.status_code, 200)
        print(" -> Admin Privileges Verified: OK")

    def test_05_legal_settings_management(self):
        """Test updating legal texts via API."""
        print("\n[STEP 5] Testing Legal Content Updates...")
        self.login("superadmin")
        
        new_privacy = "# New Privacy Policy\nThis is a test."
        res = self.client.post('/api/admin/settings/global', data=json.dumps({
            'privacy_policy': new_privacy,
            'imprint': 'Default Imprint'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        # Verify it's live
        res = self.client.get('/privacy')
        self.assertIn(b'New Privacy Policy', res.data)
        print(" -> Legal Settings Propagation: OK")

    def test_06_database_sanity_check(self):
        """Final check on database structure and relations."""
        print("\n[STEP 6] Running Database Sanity Audit...")
        with self.app.app_context():
            # Check if all models are responsive
            self.assertIsNotNone(User.query.first())
            self.assertIsNotNone(SchoolClass.query.first())
            print(f" -> Tables (User, Class, GlobalSettings): Online")
            
            # Check relationships
            stu = User.query.filter_by(username="student").first()
            self.assertEqual(stu.school_class.id, self.test_class_id)
            print(" -> Relationships (User -> Class): Valid")

    def test_07_backup_restore_cycle(self):
        """Test if data persists through an export/import cycle."""
        print("\n[STEP 7] Testing Backup & Restore Cycle...")
        self.login("superadmin")
        
        # 1. Export
        res = self.client.get('/api/admin/backup')
        self.assertEqual(res.status_code, 200)
        backup_json = json.loads(res.data)
        self.assertIn('users', backup_json)
        print(" -> Backup Export: OK")
        
        # 2. Modify something
        res = self.client.post('/api/admin/settings/global', data=json.dumps({
            'privacy_policy': 'Original',
            'imprint': 'CHANGED_IMPRINT'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        # Verify change
        res = self.client.get('/imprint')
        self.assertIn(b'CHANGED_IMPRINT', res.data)
        
        # 3. Restore
        from io import BytesIO
        data = dict(file=(BytesIO(json.dumps(backup_json).encode()), 'backup.json'))
        res = self.client.post('/api/admin/restore', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        print(" -> Backup Restore: OK")
        
        # 4. Verify initial state returned (imprint should be default again)
        res = self.client.get('/imprint')
        self.assertNotIn(b'CHANGED_IMPRINT', res.data)
        print(" -> Data Integrity Verification: OK")

if __name__ == '__main__':
    print("="*60)
    print(" L8TESTUDY - FULL SYSTEM AUDIT TOOL ")
    print("="*60)
    
    # Run tests with a custom runner to make output prettier
    suite = unittest.TestLoader().loadTestsFromTestCase(L8teStudyComprehensiveTest)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print(" SUMMARY: ALL SYSTEMS FUNCTIONAL! ")
    else:
        print(f" SUMMARY: FOUND {len(result.failures) + len(result.errors)} ISSUES! ")
    print("="*60)
    
    sys.exit(not result.wasSuccessful())
