import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    // Ramp up to 10 users over 1 minute
    { duration: '1m', target: 10 },
    // Stay at 10 users for 2 minutes
    { duration: '2m', target: 10 },
    // Ramp up to 50 users over 2 minutes
    { duration: '2m', target: 50 },
    // Stay at 50 users for 3 minutes
    { duration: '3m', target: 50 },
    // Ramp up to 100 users over 2 minutes
    { duration: '2m', target: 100 },
    // Stay at 100 users for 3 minutes
    { duration: '3m', target: 100 },
    // Ramp down to 0 users over 1 minute
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate must be below 10%
  },
};

// Base URL for the load balancer
const BASE_URL = __ENV.BASE_URL || 'http://nginx-lb';

// Test scenarios
export default function () {
  // Random user ID for testing
  const userId = Math.floor(Math.random() * 1000) + 1;
  const eventId = Math.floor(Math.random() * 100) + 1;

  // Test 1: Health Check (Light load)
  const healthCheck = http.get(`${BASE_URL}/health`);
  check(healthCheck, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  });

  // Test 2: Frontend Access (Medium load)
  const frontendResponse = http.get(`${BASE_URL}/`);
  check(frontendResponse, {
    'frontend status is 200': (r) => r.status === 200,
    'frontend response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test 3: Auth Service (Medium load)
  const authResponse = http.get(`${BASE_URL}/auth/health`);
  check(authResponse, {
    'auth service status is 200': (r) => r.status === 200,
    'auth service response time < 300ms': (r) => r.timings.duration < 300,
  });

  // Test 4: Catalog Service (Medium load)
  const catalogResponse = http.get(`${BASE_URL}/catalog/health`);
  check(catalogResponse, {
    'catalog service status is 200': (r) => r.status === 200,
    'catalog service response time < 300ms': (r) => r.timings.duration < 300,
  });

  // Test 5: Booking Service (Heavy load - simulates real booking)
  const bookingData = JSON.stringify({
    user_id: userId,
    event_id: eventId,
    seats: Math.floor(Math.random() * 4) + 1,
    timestamp: new Date().toISOString(),
  });

  const bookingResponse = http.post(`${BASE_URL}/booking/create`, bookingData, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(bookingResponse, {
    'booking service status is 200 or 201': (r) => r.status === 200 || r.status === 201,
    'booking service response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test 6: Payment Service (Heavy load - simulates payment processing)
  const paymentData = JSON.stringify({
    booking_id: Math.floor(Math.random() * 10000) + 1,
    amount: (Math.random() * 100 + 10).toFixed(2),
    currency: 'USD',
    payment_method: 'card',
    user_id: userId,
  });

  const paymentResponse = http.post(`${BASE_URL}/payment/process`, paymentData, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(paymentResponse, {
    'payment service status is 200 or 201': (r) => r.status === 200 || r.status === 201,
    'payment service response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  // Test 7: Concurrent API Calls (Stress test)
  const concurrentRequests = [
    { url: `${BASE_URL}/auth/health`, method: 'GET' },
    { url: `${BASE_URL}/catalog/health`, method: 'GET' },
    { url: `${BASE_URL}/booking/health`, method: 'GET' },
    { url: `${BASE_URL}/payment/health`, method: 'GET' },
  ];

  const responses = http.batch(concurrentRequests);
  
  responses.forEach((response, index) => {
    const isSuccess = response.status >= 200 && response.status < 300;
    if (!isSuccess) {
      errorRate.add(1);
    }
    
    check(response, {
      [`concurrent request ${index + 1} status is 2xx`]: (r) => r.status >= 200 && r.status < 300,
      [`concurrent request ${index + 1} response time < 400ms`]: (r) => r.timings.duration < 400,
    });
  });

  // Test 8: Database Stress Test (Heavy load)
  const dbStressData = JSON.stringify({
    query_type: 'complex_search',
    filters: {
      date_range: 'next_month',
      category: ['music', 'sports', 'business'],
      price_range: [0, 500],
      location: 'any',
    },
    limit: 50,
    offset: Math.floor(Math.random() * 100),
  });

  const dbStressResponse = http.post(`${BASE_URL}/catalog/search`, dbStressData, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(dbStressResponse, {
    'database stress test status is 200': (r) => r.status === 200,
    'database stress test response time < 800ms': (r) => r.timings.duration < 800,
  });

  // Random sleep between requests to simulate real user behavior
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

// Setup function (runs once at the beginning)
export function setup() {
  console.log('🚀 Starting Cloud Computing Load Test');
  console.log(`📡 Testing against: ${BASE_URL}`);
  console.log('📊 Test will run for 14 minutes with varying load');
  console.log('🎯 Testing scalability, high availability, and performance');
}

// Teardown function (runs once at the end)
export function teardown(data) {
  console.log('✅ Load test completed');
  console.log('📈 Check Prometheus and Grafana for metrics');
  console.log('🔍 Analyze performance under different load conditions');
}

// Handle errors
export function handleError(err) {
  console.error('❌ Test error:', err);
  errorRate.add(1);
}
