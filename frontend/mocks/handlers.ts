import { IItem } from "@/entities/item";
import { http, HttpResponse } from "msw";

const API_URL = process.env.API_URL;

const state: IItem[] = [];

export const handlers = [
  http.get(`${API_URL}/items/all`, async () => {
    return HttpResponse.json(state);
  }),
  http.post(`${API_URL}/items/create`, async ({ request, requestId }) => {
    const body = (await request.json()) as { title: string; file: File };
    const previewUrl = URL.createObjectURL(body.file);
    const item = {
      id: requestId,
      title: body.title,
      preview_url: previewUrl,
    } as IItem;
    state.push(item);
    return HttpResponse.json({ item });
  }),
];
