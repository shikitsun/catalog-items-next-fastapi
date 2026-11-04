import { getItems, IItem } from "@/entities/item";

export default async function Home() {
  const items: IItem[] = await getItems();

  // Handle empty states
  if (!items?.length)
    return (
      <main>
        <h1>
          No items available yet. Please, wait for catalog items are arrives
        </h1>
      </main>
    );

  return <main></main>;
}
