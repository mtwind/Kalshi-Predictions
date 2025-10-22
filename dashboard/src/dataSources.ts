export type DataSourceKey =
  | "tudum"
  | "flixpatrol"
  | "x"
  | "tiktok"
  | "reddit"
  | "gtrends"
  | "youtube"
  | "wikipedia";

export interface DataSource {
  key: DataSourceKey;
  name: string;
  category: "Popularity/Streaming" | "Social" | "Search";
  desc: string;
  docsUrl?: string;
  connected?: boolean;
}

export const DATA_SOURCES: DataSource[] = [
  {
    key: "tudum",
    name: "Netflix Tudum Top 10",
    category: "Popularity/Streaming",
    desc: "Official weekly ranks (hours viewed). Used for labels + lag features.",
    docsUrl: "https://www.netflix.com/tudum/top10",
    connected: false,
  },
  {
    key: "flixpatrol",
    name: "FlixPatrol",
    category: "Popularity/Streaming",
    desc: "Daily top charts by country for early momentum signals.",
    docsUrl: "https://flixpatrol.com/",
    connected: false,
  },
  {
    key: "x",
    name: "X (Twitter)",
    category: "Social",
    desc: "Mentions, unique authors, engagement, sentiment.",
    docsUrl: "https://developer.x.com/en/docs",
    connected: false,
  },
  {
    key: "tiktok",
    name: "TikTok",
    category: "Social",
    desc: "Hashtag views, creator counts, engagement velocity.",
    docsUrl: "https://developers.tiktok.com/",
    connected: false,
  },
  {
    key: "reddit",
    name: "Reddit",
    category: "Social",
    desc: "Posts/comments volume across subs; upvote ratios.",
    docsUrl: "https://www.reddit.com/dev/api",
    connected: false,
  },
  {
    key: "gtrends",
    name: "Google Trends",
    category: "Search",
    desc: "Relative search interest (US) with baseline normalization.",
    docsUrl: "https://trends.google.com/",
    connected: false,
  },
  {
    key: "youtube",
    name: "YouTube Analytics",
    category: "Search",
    desc: "Trailer view deltas, like ratios, comment velocity.",
    docsUrl: "https://developers.google.com/youtube/v3",
    connected: false,
  },
  {
    key: "wikipedia",
    name: "Wikipedia Pageviews",
    category: "Search",
    desc: "Daily pageview counts via Wikimedia REST API.",
    docsUrl: "https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews",
    connected: false,
  },
];
