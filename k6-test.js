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

export default function () {
  // Hit the local Docker container running inside the GitHub runner
  const res = http.get('http://localhost:8080/summary');
  
  // Verify the server actually responds with a healthy page
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
