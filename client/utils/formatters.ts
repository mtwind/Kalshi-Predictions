// client/utils/formatters.ts

export const normalizeShowName = (rawName: string): string => {
  if (!rawName) return "";
  let name = rawName;

  // 1. Remove ": Season ..." (case insensitive)
  // e.g. "Stranger Things: Season 5" -> "Stranger Things"
  name = name.split(/:\s*Season/i)[0];

  // 2. Remove trailing numbers often used in Kalshi tickers
  // e.g. "Stranger Things 5" -> "Stranger Things"
  // Note: We use \b to ensure we don't cut off numbers inside a word if that ever happens
  name = name.replace(/\s+\d+$/, "");

  return name.trim();
};

export const formatDate = (date: Date): string => {
  return date.toISOString().split("T")[0];
};

export const getTimeAgo = (dateString: string): string => {
  const diff = new Date().getTime() - new Date(dateString).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
};
