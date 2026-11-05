import { IItem } from "@/entities/item";
import { http, HttpResponse } from "msw";
import { faker } from "@faker-js/faker";

const API_URL = process.env.API_URL;

const state: IItem[] = Array.from({
  length: Math.floor(Math.random() * 1000),
}).map(() => {
  return {
    id: faker.string.uuid(),
    preview_url: faker.image.dataUri(),
    title: faker.food.fruit(),
  } as IItem;
});

export const handlers = [
  http.get(`${API_URL}/items/all`, async () => {
    return HttpResponse.json(state);
  }),
];
