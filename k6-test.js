import http from 'k6/http';
import { check } from 'k6';

export const options = {
  // 1. Stress Testing: Simulate your Peak Throughput of 15 RPS
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 15,          // 15 requests
      timeUnit: '1s',    // per 1 second
      duration: '20s',   // run the test for 20 seconds
      preAllocatedVUs: 20, // keep 20 virtual users on standby
      maxVUs: 50,
    },
  },
  
  // 2. The Quality Gate: Defining your strict SLAs
  thresholds: {
    // 99% of all requests must succeed (status 200)
    http_req_failed: ['rate<0.01'], 
    // P95 API Latency must strictly be under 200ms
    http_req_duration: ['p(95)<200'], 
  },
};

// --- NEW SECURITY LOGIC ---
// This runs exactly once before the stress test begins.
export function setup() {
  // 1. Register a load testing user (FastAPI returns 400 if it already exists, which is fine)
  const regPayload = JSON.stringify({ username: 'load_tester', password: 'load_password' });
  http.post('http://localhost:8080/register', regPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  // 2. Log in to get the HTTP-Only cookie. 
  // Because we pass a JS object, k6 automatically formats this as 'application/x-www-form-urlencoded' (Form Data)
  const loginPayload = { username: 'load_tester', password: 'load_password' };
  const loginRes = http.post('http://localhost:8080/login', loginPayload);

  // 3. Extract the cookie value from the server's response
  const tokenCookie = loginRes.cookies.access_token[0].value;
  
  // 4. Return it so the Virtual Users can share it
  return { cookie: tokenCookie };
}

// This is the main function that fires 301 times.
// k6 automatically injects the data returned from setup() into this function.
export default function (data) {
  
  // 5. Attach the cookie to the request to bypass the FastAPI bouncer
  const res = http.get('http://localhost:8080/summary', {
    cookies: {
      access_token: data.cookie 
    }
  });
  
  // Verify the server actually responds with a healthy page
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}