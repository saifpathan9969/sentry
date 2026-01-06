"""
Unit Tests for False Positive SQL Injection Fix
Tests platform detection and SQL test skipping functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ai_pentest_brain_complete import AIPentestBrain
from enhanced_vulnerability_detector import EnhancedVulnerabilityDetector


class TestPlatformDetection(unittest.TestCase):
    """Test platform detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.brain = AIPentestBrain()
    
    @patch('requests.get')
    def test_firebase_detection_from_url(self, mock_get):
        """Test Firebase detection from URL"""
        # Mock response
        mock_response = Mock()
        mock_response.text = '<html><body>Test page</body></html>'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        # Test Firebase URL
        platform_info = self.brain._detect_platform_and_database('https://example.firebaseapp.com')
        
        self.assertEqual(platform_info['platform'], 'firebase')
        self.assertEqual(platform_info['database_type'], 'nosql')
        self.assertTrue(platform_info['skip_sql_tests'])
        self.assertGreaterEqual(platform_info['confidence'], 0.6)  # Accept 0.6+ (2 indicators = 0.7)
        self.assertIn('indicators_found', platform_info)
        self.assertGreater(len(platform_info['indicators_found']), 0)
    
    @patch('requests.get')
    def test_firebase_detection_from_response(self, mock_get):
        """Test Firebase detection from response content"""
        # Mock response with Firebase indicators
        mock_response = Mock()
        mock_response.text = '''
            <html>
            <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js"></script>
            <script>
                const firebaseConfig = {
                    apiKey: "test",
                    authDomain: "test.firebaseapp.com"
                };
            </script>
            </html>
        '''
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        self.assertEqual(platform_info['platform'], 'firebase')
        self.assertEqual(platform_info['database_type'], 'nosql')
        self.assertTrue(platform_info['skip_sql_tests'])
        self.assertGreaterEqual(platform_info['confidence'], 0.8)
    
    @patch('requests.get')
    def test_mongodb_detection(self, mock_get):
        """Test MongoDB detection"""
        mock_response = Mock()
        mock_response.text = 'mongodb connection error: failed to connect to mongodb://localhost:27017'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        self.assertEqual(platform_info['database_type'], 'nosql')
        self.assertTrue(platform_info['skip_sql_tests'])
        self.assertGreaterEqual(platform_info['confidence'], 0.8)
    
    @patch('requests.get')
    def test_dynamodb_detection(self, mock_get):
        """Test DynamoDB detection"""
        mock_response = Mock()
        mock_response.text = 'dynamodb error: table not found'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        self.assertEqual(platform_info['database_type'], 'nosql')
        self.assertTrue(platform_info['skip_sql_tests'])
    
    @patch('requests.get')
    def test_sql_database_detection(self, mock_get):
        """Test SQL database detection"""
        mock_response = Mock()
        mock_response.text = 'mysql error: connection failed'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        self.assertEqual(platform_info['database_type'], 'sql')
        self.assertFalse(platform_info['skip_sql_tests'])
        self.assertGreaterEqual(platform_info['confidence'], 0.8)
    
    @patch('requests.get')
    def test_aws_platform_no_auto_skip(self, mock_get):
        """Test AWS platform detection does NOT auto-skip SQL tests"""
        mock_response = Mock()
        mock_response.text = '<html>Test page</html>'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.amazonaws.com')
        
        self.assertEqual(platform_info['platform'], 'aws')
        # AWS should NOT auto-skip SQL tests (supports both SQL and NoSQL)
        self.assertFalse(platform_info['skip_sql_tests'])
    
    @patch('requests.get')
    def test_unknown_platform_default_behavior(self, mock_get):
        """Test unknown platform uses safe defaults"""
        mock_response = Mock()
        mock_response.text = '<html>Generic page</html>'
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        self.assertEqual(platform_info['platform'], 'unknown')
        self.assertEqual(platform_info['database_type'], 'unknown')
        # Should run all tests when uncertain (safe default)
        self.assertFalse(platform_info['skip_sql_tests'])
    
    @patch('requests.get')
    def test_confidence_score_calculation(self, mock_get):
        """Test confidence score increases with more indicators"""
        mock_response = Mock()
        mock_response.text = '''
            firebase firestore firebaseio.com firebase-messaging
            gstatic.com/firebasejs firebase-config
        '''
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        platform_info = self.brain._detect_platform_and_database('https://example.firebaseapp.com')
        
        # Multiple indicators should result in high confidence
        self.assertGreaterEqual(platform_info['confidence'], 0.8)
        self.assertGreater(len(platform_info['indicators_found']), 3)
    
    @patch('requests.get')
    def test_network_error_handling(self, mock_get):
        """Test graceful handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        platform_info = self.brain._detect_platform_and_database('https://example.com')
        
        # Should return safe defaults on error
        self.assertEqual(platform_info['platform'], 'unknown')
        self.assertFalse(platform_info['skip_sql_tests'])


class TestSQLTestSkipping(unittest.TestCase):
    """Test SQL injection test skipping based on platform"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.brain = AIPentestBrain()
    
    @patch('requests.post')
    def test_sql_test_skipped_on_nosql(self, mock_post):
        """Test SQL injection tests are skipped on NoSQL platforms"""
        platform_info = {
            'skip_sql_tests': True,
            'platform': 'firebase',
            'database_type': 'nosql',
            'confidence': 0.9
        }
        
        result = self.brain._test_sql_injection('https://example.com/login', platform_info)
        
        # Should return None (skipped)
        self.assertIsNone(result)
        # Should NOT make any HTTP requests
        mock_post.assert_not_called()
    
    @patch('requests.post')
    def test_sql_test_runs_on_sql_platform(self, mock_post):
        """Test SQL injection tests run on SQL platforms"""
        platform_info = {
            'skip_sql_tests': False,
            'platform': 'unknown',
            'database_type': 'sql',
            'confidence': 0.8
        }
        
        # Mock response without SQL errors
        mock_response = Mock()
        mock_response.text = 'Login failed'
        mock_post.return_value = mock_response
        
        result = self.brain._test_sql_injection('https://example.com/login', platform_info)
        
        # Should make HTTP requests (tests run)
        self.assertGreater(mock_post.call_count, 0)
    
    @patch('requests.post')
    def test_sql_test_runs_without_platform_info(self, mock_post):
        """Test backward compatibility - tests run when no platform_info provided"""
        # Mock response
        mock_response = Mock()
        mock_response.text = 'Login failed'
        mock_post.return_value = mock_response
        
        result = self.brain._test_sql_injection('https://example.com/login', None)
        
        # Should make HTTP requests (backward compatible)
        self.assertGreater(mock_post.call_count, 0)


class TestEnhancedVulnerabilityDetector(unittest.TestCase):
    """Test EnhancedVulnerabilityDetector platform integration"""
    
    def test_detector_accepts_platform_info(self):
        """Test detector accepts platform_info in constructor"""
        platform_info = {
            'skip_sql_tests': True,
            'platform': 'firebase',
            'database_type': 'nosql'
        }
        
        detector = EnhancedVulnerabilityDetector(platform_info=platform_info)
        
        self.assertEqual(detector.platform_info, platform_info)
    
    def test_detector_skips_sql_tests_on_nosql(self):
        """Test detector skips SQL tests when platform is NoSQL"""
        platform_info = {
            'skip_sql_tests': True,
            'platform': 'mongodb',
            'database_type': 'nosql'
        }
        
        detector = EnhancedVulnerabilityDetector(platform_info=platform_info)
        
        # Mock the _test_sql_injection method to track if it's called
        with patch.object(detector, '_test_sql_injection') as mock_sql_test:
            vulns = detector._check_injection_vulnerabilities('https://example.com')
            
            # SQL injection test should NOT be called
            mock_sql_test.assert_not_called()
    
    def test_detector_runs_sql_tests_on_sql_platform(self):
        """Test detector runs SQL tests on SQL platforms"""
        platform_info = {
            'skip_sql_tests': False,
            'platform': 'unknown',
            'database_type': 'sql'
        }
        
        detector = EnhancedVulnerabilityDetector(platform_info=platform_info)
        
        # Mock the _test_sql_injection method
        with patch.object(detector, '_test_sql_injection', return_value=None) as mock_sql_test:
            vulns = detector._check_injection_vulnerabilities('https://example.com')
            
            # SQL injection test SHOULD be called
            self.assertGreater(mock_sql_test.call_count, 0)


class TestSQLErrorPatterns(unittest.TestCase):
    """Test improved SQL error detection patterns"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.brain = AIPentestBrain()
    
    @patch('requests.post')
    def test_specific_sql_error_detected(self, mock_post):
        """Test specific SQL error patterns are detected"""
        mock_response = Mock()
        mock_response.text = 'You have an error in your SQL syntax near mysql_query'
        mock_post.return_value = mock_response
        
        result = self.brain._test_sql_injection('https://example.com/login')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'sql_injection')
        self.assertIn('evidence', result)
        self.assertIsInstance(result['evidence'], dict)
        self.assertIn('matched_pattern', result['evidence'])
    
    @patch('requests.post')
    def test_generic_sql_word_not_flagged(self, mock_post):
        """Test generic 'sql' word doesn't trigger false positive"""
        mock_response = Mock()
        mock_response.text = 'Learn SQL programming at our website. SQL tutorials available.'
        mock_post.return_value = mock_response
        
        result = self.brain._test_sql_injection('https://example.com/login')
        
        # Should NOT flag as SQL injection (no specific error patterns)
        self.assertIsNone(result)
    
    @patch('requests.post')
    def test_authentication_bypass_requires_sql_indicators(self, mock_post):
        """Test authentication bypass requires SQL-specific indicators"""
        # Test 1: Login success WITHOUT SQL indicators - should NOT flag
        mock_response = Mock()
        mock_response.text = 'Login successful! Welcome to your dashboard.'
        mock_post.return_value = mock_response
        
        result = self.brain._test_sql_injection('https://example.com/login')
        self.assertIsNone(result)
        
        # Test 2: Login success WITH SQL indicators - should flag
        mock_response.text = 'Login successful! Connected to mysql database.'
        result = self.brain._test_sql_injection('https://example.com/login')
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'sql_injection')


if __name__ == '__main__':
    unittest.main()
