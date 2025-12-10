// client/services/api.ts
const API_BASE = "http://localhost:8000"; // Ensure this matches your FastAPI port

// --- KALSHI ---
export const fetchKalshiTop = async (limit = 5) => {
  const res = await fetch(`${API_BASE}/kalshi/netflix/top?limit=${limit}`);
  return res.json();
};

// --- TRENDS ---
export const fetchTrends = async (term: string) => {
  const res = await fetch(`${API_BASE}/trends/interest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      search_term: term,
      start_date: "2025-12-01",
      end_date: "2025-12-10", // You might want to make these dynamic arguments
      geo: "US",
    }),
  });
  return res.json();
};

// --- YOUTUBE ---
export const fetchYoutubeSearch = async (query: string) => {
  const res = await fetch(`${API_BASE}/youtube/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: query,
      max_results: 5,
      order: "relevance",
    }),
  });
  return res.json();
};

// --- WIKIPEDIA ---
export const fetchWikiPageviews = async (
  article: string,
  startDate: string,
  endDate: string
) => {
  const res = await fetch(`${API_BASE}/wikipedia/pageviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      article_title: article,
      start_date: startDate,
      end_date: endDate,
    }),
  });
  return res.json();
};

// --- TMDB ---
export const fetchTmdbTrending = async () => {
  const res = await fetch(`${API_BASE}/tmdb/tv/trending?time_window=week`);
  return res.json();
};

// --- NEWS ---
export const fetchGoogleNews = async (
  query: string,
  fromDate?: string,
  toDate?: string
) => {
  const res = await fetch(`${API_BASE}/google-news/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: query,
      from_date: fromDate,
      to_date: toDate,
      max_results: 100, // Request maximum articles for better sample size
      sort_by: "publishedAt",
    }),
  });
  return res.json();
};
