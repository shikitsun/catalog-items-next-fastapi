import { IItem } from "../item";

export function BaseItemCard({ preview_url, title }: IItem) {
  return (
    <section className="flex flex-col items-center rounded-sm transition-all hover:shadow-lg dark:shadow-zinc-400 group">
      <div
        className="w-80 max-w-dvw aspect-video bg-contain group-hover:scale-105 transition-all duration-500 rounded-sm"
        style={{ backgroundImage: `url(${preview_url})` }}
      ></div>

      <div className="px-2 py-2 w-full">
        <h3>{title}</h3>
      </div>
    </section>
  );
}
