import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '5m', target: 200 },
    { duration: '5m', target: 10 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};
const urls = [
  "http://localhost:5050/",
  "http://localhost:5050/fail",
  "http://localhost:5050/slow",
  "http://localhost:5050/random"
];

export default function () {
  let responses = http.batch(urls.map(url => ['GET', url]));

  responses.forEach((res, index) => {
    if (res.status !== 200) {
      console.log(`درخواست به ${urls[index]} با کد ${res.status} شکست خورد`);
    }
  });

  sleep(1);
}