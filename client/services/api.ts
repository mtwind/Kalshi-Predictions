// client/services/api.ts
const API_BASE = "http://localhost:8000"; // Ensure this matches your FastAPI port

// --- KALSHI ---
export const fetchKalshiTop = async (limit = 5) => {
  const res = await fetch(`${API_BASE}/kalshi/netflix/top?limit=${limit}`);
  return res.json();
};

// --- TRENDS ---
export const fetchTrends = async (
  term: string,
  startDate?: string,
  endDate?: string
) => {
  const res = await fetch(`${API_BASE}/trends/interest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      search_term: term,
      start_date: startDate || "2025-12-01",
      end_date: endDate || "2025-12-31",
      geo: "US",
    }),
  });
  return res.json();
};

export const fetchTrendsCompare = async (
  terms: string[],
  startDate?: string,
  endDate?: string
) => {
  const res = await fetch(`${API_BASE}/trends/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      search_terms: terms,
      start_date: startDate,
      end_date: endDate,
      geo: "US",
    }),
  });
  return res.json();
};

// --- YOUTUBE ---
export const fetchYoutubeAnalysis = async (showName: string) => {
  const res = await fetch(`${API_BASE}/youtube/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ show_name: showName }),
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

// NEW: Analysis Endpoint
export const fetchTmdbAnalysis = async (showName: string) => {
  const res = await fetch(`${API_BASE}/tmdb/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ show_name: showName }),
  });
  return res.json();
};

export const fetchTmdbSearch = async (query: string) => {
  // ... (keep existing if needed for other things, but Card will use Analysis now)
  const res = await fetch(`${API_BASE}/tmdb/tv/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, page: 1 }),
  });
  return res.json();
};

export const fetchTmdbDetails = async (tvId: number) => {
  const res = await fetch(`${API_BASE}/tmdb/tv/details/${tvId}`);
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
