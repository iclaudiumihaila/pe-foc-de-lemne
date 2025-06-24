const http = require('http');

console.log('Testing API endpoints from localhost...\n');

// Test 1: Direct API call without auth
const testWithoutAuth = () => {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 8000,
      path: '/api/admin/orders',
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('Test 1 - Direct API call without auth:');
        console.log('Status:', res.statusCode);
        console.log('Headers:', res.headers);
        console.log('Body:', data.substring(0, 200));
        console.log('\n---\n');
        resolve();
      });
    });

    req.on('error', (e) => {
      console.error('Test 1 Error:', e.message);
      resolve();
    });

    req.end();
  });
};

// Test 2: Check CORS headers with OPTIONS
const testCorsOptions = () => {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 8000,
      path: '/api/admin/orders',
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'authorization,content-type'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('Test 2 - CORS OPTIONS request:');
        console.log('Status:', res.statusCode);
        console.log('Headers:', res.headers);
        console.log('Body:', data || '(empty)');
        console.log('\n---\n');
        resolve();
      });
    });

    req.on('error', (e) => {
      console.error('Test 2 Error:', e.message);
      resolve();
    });

    req.end();
  });
};

// Test 3: Check products endpoint (public)
const testPublicEndpoint = () => {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 8000,
      path: '/api/products',
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Origin': 'http://localhost:3000'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('Test 3 - Public products endpoint:');
        console.log('Status:', res.statusCode);
        console.log('Headers:', res.headers);
        console.log('Body length:', data.length);
        console.log('CORS header:', res.headers['access-control-allow-origin']);
        console.log('\n---\n');
        resolve();
      });
    });

    req.on('error', (e) => {
      console.error('Test 3 Error:', e.message);
      resolve();
    });

    req.end();
  });
};

// Run all tests sequentially
(async () => {
  await testWithoutAuth();
  await testCorsOptions();
  await testPublicEndpoint();
  
  console.log('\nDiagnosis:');
  console.log('1. Check if Access-Control-Allow-Origin matches the Origin header');
  console.log('2. For localhost:3000, the backend should respond with "http://localhost:3000"');
  console.log('3. Current issue: Backend might be responding with IP address instead of localhost');
})();