import { http, HttpResponse } from "msw";

const API_URL = process.env.API_URL;

export const handlers = [
  http.get(`${API_URL}/items/all`, async () => {
    return HttpResponse.json([]);
  }),
];
