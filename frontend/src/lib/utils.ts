export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function timeAgo(value: string | number | null | undefined): string {
  if (value == null) return "just now";
  const then = typeof value === "string" ? new Date(value).getTime() : value;
  if (Number.isNaN(then)) return "just now";
  const seconds = Math.round((Date.now() - then) / 1000);
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  const divisions: Array<[number, Intl.RelativeTimeFormatUnit]> = [
    [60, "second"],
    [60, "minute"],
    [24, "hour"],
    [7, "day"],
    [4.35, "week"],
    [12, "month"],
    [Number.POSITIVE_INFINITY, "year"],
  ];
  let divisor = 1;
  let unit: Intl.RelativeTimeFormatUnit = "second";
  for (const [amount, u] of divisions) {
    if (seconds < amount) {
      unit = u;
      break;
    }
    divisor = amount;
  }
  return rtf.format(-Math.round(seconds / divisor), unit);
}

export function scoreColor(score: number): string {
  if (score < 40) return "var(--critical)";
  if (score < 70) return "var(--warning)";
  return "var(--success)";
}

export function scoreVerdict(score: number): string {
  if (score < 40) return "Needs attention";
  if (score < 70) return "Fair";
  return "Good";
}

export function baseName(filePath: string): string {
  return filePath.split("/").pop() ?? filePath;
}

export function titleCase(value: string): string {
  return value.replace(/(^|\s)\S/g, (c) => c.toUpperCase());
}

export function slugify(value: string): string {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug;
}
