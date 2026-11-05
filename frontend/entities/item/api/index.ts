import { IItem } from "../model";

export async function getItems(): Promise<IItem[]> {
  const resp = await fetch(`${process.env.API_URL}/items/all`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!resp.ok) throw new Error(`${resp.status}`);
  return resp.json();
}
