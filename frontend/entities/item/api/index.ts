import { IItem } from "../model";

export async function getItems(): Promise<IItem[]> {
  return (
    await fetch(`${process.env.API_URL}/items/all`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
  ).json();
}
