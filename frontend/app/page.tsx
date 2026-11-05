import { getItems, IItem } from "@/entities/item";
import { BaseItemCard } from "@/entities/ui/BaseItemCard";

export const dynamic = "force-dynamic";

export default async function Home() {
  const items: IItem[] = await getItems();

  // Handle empty states
  if (!items?.length)
    return (
      <main className="px-5 py-5">
        <h1>Catalog</h1>
        <h2>
          No items available yet. Please, wait for catalog items are arrives
        </h2>
      </main>
    );

  return (
    <main className="flex flex-wrap items-center justify-center gap-x-5 gap-y-5 px-5 py-5">
      <h1>Catalog</h1>
      {items.map((item) => (
        <BaseItemCard key={item.id} {...item} />
      ))}
    </main>
  );
}
