import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 20, // 20 concurrent virtual users
  duration: '10s', // 10 seconds smoke load test
  thresholds: {
    http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    http_req_duration: ['p(95)<400', 'p(99)<800'], // 95% requests < 400ms, 99% requests < 800ms
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:3000';

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(0.5);
}
