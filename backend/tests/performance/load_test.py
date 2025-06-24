"""
Load Testing for Local Producer Web Application

This module provides comprehensive load testing for the Flask application
to ensure it can handle expected traffic loads and scales appropriately.
"""

import asyncio
import aiohttp
import time
import statistics
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadTestConfig:
    """Load testing configuration"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api"
        
        # Test scenarios
        self.scenarios = {
            'normal_load': {
                'users': 50,
                'duration': 300,  # 5 minutes
                'ramp_up': 30     # 30 seconds
            },
            'peak_load': {
                'users': 200,
                'duration': 600,  # 10 minutes
                'ramp_up': 60     # 60 seconds
            },
            'stress_test': {
                'users': 500,
                'duration': 300,  # 5 minutes
                'ramp_up': 30     # 30 seconds
            }
        }
        
        # Performance thresholds
        self.thresholds = {
            'avg_response_time': 500,  # 500ms
            'p95_response_time': 1000, # 1 second
            'p99_response_time': 2000, # 2 seconds
            'error_rate': 0.01,        # 1% error rate
            'throughput': 100          # 100 requests per second
        }


class LoadTestMetrics:
    """Metrics collection for load testing"""
    
    def __init__(self):
        self.requests = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def add_request(self, endpoint: str, method: str, response_time: float, 
                   status_code: int, error: Optional[str] = None):
        """Add a request result to metrics"""
        request_data = {
            'timestamp': time.time(),
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code,
            'error': error
        }
        
        self.requests.append(request_data)
        
        if error or status_code >= 400:
            self.errors.append(request_data)
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate performance statistics"""
        if not self.requests:
            return {}
        
        response_times = [req['response_time'] for req in self.requests]
        successful_requests = [req for req in self.requests if req['status_code'] < 400]
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        stats = {
            'total_requests': len(self.requests),
            'successful_requests': len(successful_requests),
            'failed_requests': len(self.errors),
            'error_rate': len(self.errors) / len(self.requests) if self.requests else 0,
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99),
            'throughput': len(self.requests) / total_duration if total_duration > 0 else 0,
            'duration': total_duration
        }
        
        # Add endpoint-specific statistics
        endpoints = {}
        for req in self.requests:
            endpoint = req['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(req['response_time'])
        
        for endpoint, times in endpoints.items():
            endpoints[endpoint] = {
                'count': len(times),
                'avg_response_time': statistics.mean(times),
                'p95_response_time': self._percentile(times, 95)
            }
        
        stats['endpoints'] = endpoints
        
        return stats
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class LoadTestUser:
    """Simulates a user session"""
    
    def __init__(self, user_id: int, session: aiohttp.ClientSession, 
                 base_url: str, metrics: LoadTestMetrics):
        self.user_id = user_id
        self.session = session
        self.base_url = base_url
        self.metrics = metrics
        self.user_session_id = f"test-session-{user_id}-{int(time.time())}"
    
    async def run_scenario(self, duration: int):
        """Run user scenario for specified duration"""
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                # Choose random user journey
                journey = random.choice([
                    self.browse_products_journey,
                    self.search_products_journey,
                    self.cart_journey,
                    self.admin_journey
                ])
                
                await journey()
                
                # Random wait between actions (1-5 seconds)
                await asyncio.sleep(random.uniform(1, 5))
                
            except Exception as e:
                logger.error(f"User {self.user_id} error: {e}")
                await asyncio.sleep(1)
    
    async def browse_products_journey(self):
        """Simulate browsing products"""
        # Get categories
        await self.make_request('GET', '/api/categories')
        
        # Get products
        await self.make_request('GET', '/api/products')
        
        # Get specific product
        await self.make_request('GET', '/api/products/1')
        
        # Search products
        search_terms = ['mere', 'roșii', 'brânză', 'lapte']
        term = random.choice(search_terms)
        await self.make_request('GET', f'/api/products?search={term}')
    
    async def search_products_journey(self):
        """Simulate product search"""
        search_terms = ['fructe', 'legume', 'lactate', 'carne']
        
        for _ in range(random.randint(1, 3)):
            term = random.choice(search_terms)
            await self.make_request('GET', f'/api/products?search={term}')
            
            # Filter by category
            categories = ['Fructe', 'Legume', 'Produse lactate']
            category = random.choice(categories)
            await self.make_request('GET', f'/api/products?category={category}')
    
    async def cart_journey(self):
        """Simulate cart operations"""
        # Add items to cart
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, 20)
            quantity = random.randint(1, 3)
            
            cart_data = {
                'product_id': str(product_id),
                'quantity': quantity,
                'session_id': self.user_session_id
            }
            
            await self.make_request('POST', '/api/cart', json=cart_data)
        
        # Get cart contents
        await self.make_request('GET', f'/api/cart/{self.user_session_id}')
        
        # Simulate SMS verification (mock)
        phone_data = {'phone_number': '+40721234567'}
        await self.make_request('POST', '/api/sms/verify', json=phone_data)
    
    async def admin_journey(self):
        """Simulate admin operations"""
        # Admin login (mock - we'll test the endpoint but won't actually auth)
        login_data = {
            'username': 'test_admin',
            'password': 'test_password'
        }
        await self.make_request('POST', '/api/auth/login', json=login_data)
    
    async def make_request(self, method: str, endpoint: str, 
                          json: Optional[Dict] = None, 
                          params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request and record metrics"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                try:
                    data = await response.json()
                except:
                    data = None
                
                self.metrics.add_request(
                    endpoint=endpoint,
                    method=method,
                    response_time=response_time,
                    status_code=response.status,
                    error=None if response.status < 400 else f"HTTP {response.status}"
                )
                
                return data
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.metrics.add_request(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                error=str(e)
            )
            return None


class LoadTester:
    """Main load testing orchestrator"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics = LoadTestMetrics()
    
    async def run_load_test(self, scenario_name: str) -> Dict[str, Any]:
        """Run load test scenario"""
        scenario = self.config.scenarios[scenario_name]
        
        logger.info(f"Starting load test: {scenario_name}")
        logger.info(f"Users: {scenario['users']}, Duration: {scenario['duration']}s")
        
        self.metrics = LoadTestMetrics()
        self.metrics.start_time = time.time()
        
        # Create HTTP session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=scenario['users'] * 2,
            limit_per_host=scenario['users'],
            keepalive_timeout=30
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create and start users with ramp-up
            tasks = []
            users_per_second = scenario['users'] / scenario['ramp_up']
            
            for i in range(scenario['users']):
                user = LoadTestUser(i, session, self.config.base_url, self.metrics)
                
                # Calculate delay for ramp-up
                delay = i / users_per_second
                task = asyncio.create_task(self._delayed_user_start(user, delay, scenario['duration']))
                tasks.append(task)
            
            # Wait for all users to complete
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.metrics.end_time = time.time()
        
        # Calculate and return statistics
        stats = self.metrics.calculate_statistics()
        stats['scenario'] = scenario_name
        stats['config'] = scenario
        
        logger.info(f"Load test completed: {scenario_name}")
        logger.info(f"Total requests: {stats['total_requests']}")
        logger.info(f"Average response time: {stats['avg_response_time']:.2f}ms")
        logger.info(f"Error rate: {stats['error_rate']:.2%}")
        
        return stats
    
    async def _delayed_user_start(self, user: LoadTestUser, delay: float, duration: int):
        """Start user with delay for ramp-up"""
        await asyncio.sleep(delay)
        await user.run_scenario(duration)
    
    def validate_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance against thresholds"""
        validation = {
            'passed': True,
            'failed_metrics': [],
            'warnings': []
        }
        
        # Check each threshold
        checks = [
            ('avg_response_time', stats['avg_response_time'], self.config.thresholds['avg_response_time']),
            ('p95_response_time', stats['p95_response_time'], self.config.thresholds['p95_response_time']),
            ('p99_response_time', stats['p99_response_time'], self.config.thresholds['p99_response_time']),
            ('error_rate', stats['error_rate'], self.config.thresholds['error_rate']),
            ('throughput', stats['throughput'], self.config.thresholds['throughput'])
        ]
        
        for metric, actual, threshold in checks:
            if metric == 'throughput':
                # Throughput should be at least the threshold
                if actual < threshold:
                    validation['passed'] = False
                    validation['failed_metrics'].append({
                        'metric': metric,
                        'actual': actual,
                        'threshold': threshold,
                        'status': 'FAILED'
                    })
            elif metric == 'error_rate':
                # Error rate should be below threshold
                if actual > threshold:
                    validation['passed'] = False
                    validation['failed_metrics'].append({
                        'metric': metric,
                        'actual': actual,
                        'threshold': threshold,
                        'status': 'FAILED'
                    })
            else:
                # Response times should be below threshold
                if actual > threshold:
                    if actual > threshold * 1.5:
                        validation['passed'] = False
                        validation['failed_metrics'].append({
                            'metric': metric,
                            'actual': actual,
                            'threshold': threshold,
                            'status': 'FAILED'
                        })
                    else:
                        validation['warnings'].append({
                            'metric': metric,
                            'actual': actual,
                            'threshold': threshold,
                            'status': 'WARNING'
                        })
        
        return validation


def run_load_tests():
    """Run all load test scenarios"""
    config = LoadTestConfig()
    tester = LoadTester(config)
    
    results = {}
    
    async def run_all_scenarios():
        for scenario_name in config.scenarios.keys():
            try:
                stats = await tester.run_load_test(scenario_name)
                validation = tester.validate_performance(stats)
                
                results[scenario_name] = {
                    'stats': stats,
                    'validation': validation,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Log results
                logger.info(f"\n{'='*50}")
                logger.info(f"SCENARIO: {scenario_name}")
                logger.info(f"{'='*50}")
                logger.info(f"Total Requests: {stats['total_requests']}")
                logger.info(f"Successful: {stats['successful_requests']}")
                logger.info(f"Failed: {stats['failed_requests']}")
                logger.info(f"Error Rate: {stats['error_rate']:.2%}")
                logger.info(f"Avg Response Time: {stats['avg_response_time']:.2f}ms")
                logger.info(f"P95 Response Time: {stats['p95_response_time']:.2f}ms")
                logger.info(f"P99 Response Time: {stats['p99_response_time']:.2f}ms")
                logger.info(f"Throughput: {stats['throughput']:.2f} req/s")
                logger.info(f"Duration: {stats['duration']:.2f}s")
                
                if validation['passed']:
                    logger.info("✅ PERFORMANCE VALIDATION: PASSED")
                else:
                    logger.error("❌ PERFORMANCE VALIDATION: FAILED")
                    for failed in validation['failed_metrics']:
                        logger.error(f"  {failed['metric']}: {failed['actual']:.2f} > {failed['threshold']:.2f}")
                
                if validation['warnings']:
                    logger.warning("⚠️ PERFORMANCE WARNINGS:")
                    for warning in validation['warnings']:
                        logger.warning(f"  {warning['metric']}: {warning['actual']:.2f} > {warning['threshold']:.2f}")
                
                # Wait between scenarios
                if scenario_name != list(config.scenarios.keys())[-1]:
                    logger.info("Waiting 30 seconds before next scenario...")
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.error(f"Failed to run scenario {scenario_name}: {e}")
                results[scenario_name] = {
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
    
    # Run the tests
    asyncio.run(run_all_scenarios())
    
    # Save results to file
    results_file = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nResults saved to: {results_file}")
    
    # Summary
    passed_scenarios = sum(1 for r in results.values() if r.get('validation', {}).get('passed', False))
    total_scenarios = len([r for r in results.values() if 'stats' in r])
    
    logger.info(f"\n{'='*50}")
    logger.info(f"LOAD TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Scenarios Passed: {passed_scenarios}/{total_scenarios}")
    
    if passed_scenarios == total_scenarios:
        logger.info("🎉 ALL LOAD TESTS PASSED!")
        return 0
    else:
        logger.error("💥 SOME LOAD TESTS FAILED!")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_load_tests()
    sys.exit(exit_code)