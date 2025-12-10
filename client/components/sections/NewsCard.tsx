// client/components/sections/NewsCard.tsx
"use client";

import ArticleIcon from "@mui/icons-material/Article";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import RefreshIcon from "@mui/icons-material/Refresh";
import ScoreIcon from "@mui/icons-material/Score";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  Stack,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";

import { fetchKalshiTop, fetchNewsAnalysis } from "../../services/api";
import { normalizeShowName } from "../../utils/formatters";

interface NewsMetrics {
  show_name: string;
  news_score: number;
  sentiment_score: number;
  article_count: number;
  top_articles: {
    title: string;
    url: string;
    source_name: string;
  }[];
}

interface Props {
  refreshTrigger: number;
}

export default function NewsCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("Initializing...");
  const [data, setData] = useState<NewsMetrics[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setLoadingStatus("Checking news outlets...");
    setError(null);
    setData([]);

    try {
      const kalshiData = await fetchKalshiTop(5);
      if (!kalshiData.markets) throw new Error("No markets found");

      const uniqueShows = new Set<string>();
      kalshiData.markets.forEach((m: any) => {
        const cleanName = normalizeShowName(m.subtitle || m.title || "");
        if (cleanName) uniqueShows.add(cleanName);
      });

      const shows = Array.from(uniqueShows);
      const results: NewsMetrics[] = [];

      for (let i = 0; i < shows.length; i++) {
        const show = shows[i];
        setLoadingStatus(
          `Reading headlines for ${show} (${i + 1}/${shows.length})...`
        );

        try {
          const analysis = await fetchNewsAnalysis(show);
          // Check that we actually got a valid analysis object back
          if (analysis && typeof analysis.news_score === "number") {
            results.push(analysis);
          }
        } catch (e) {
          console.warn(`Failed News analysis for ${show}`, e);
        }
      }

      results.sort((a, b) => b.news_score - a.news_score);
      setData(results);
    } catch (err) {
      console.error(err);
      setError("Failed to load News metrics");
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return "success.main";
    if (score < -0.1) return "error.main";
    return "text.secondary";
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<NewspaperIcon color="primary" />}
        title="News Sentiment"
        subheader="Media Coverage & Scoring"
        action={
          <IconButton onClick={loadData} disabled={loading} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
        }
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        {loading ? (
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="center"
            alignItems="center"
            height={200}
            gap={2}
          >
            <CircularProgress size={30} />
            <Typography variant="caption" color="text.secondary">
              {loadingStatus}
            </Typography>
          </Box>
        ) : error ? (
          <Box p={2} textAlign="center">
            <Typography color="error" variant="body2">
              {error}
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {data.map((item, index) => (
              <React.Fragment key={item.show_name}>
                <ListItem sx={{ display: "block", py: 2 }}>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    mb={1.5}
                  >
                    <Typography variant="subtitle2" fontWeight="bold">
                      {item.show_name}
                    </Typography>
                    <Chip
                      icon={<ScoreIcon />}
                      label={`Score: ${item.news_score}`}
                      size="small"
                      color={item.news_score > 60 ? "success" : "primary"}
                      variant="filled"
                    />
                  </Box>

                  {/* Sentiment Bar */}
                  <Box mb={1}>
                    <Box display="flex" justifyContent="space-between" mb={0.5}>
                      <Typography variant="caption" color="text.secondary">
                        Negative
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Positive
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={((item.sentiment_score + 1) / 2) * 100}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: "#ffebee",
                        "& .MuiLinearProgress-bar": {
                          bgcolor: getSentimentColor(item.sentiment_score),
                        },
                      }}
                    />
                    <Typography
                      variant="caption"
                      display="block"
                      textAlign="center"
                      mt={0.5}
                      fontWeight="bold"
                      color={getSentimentColor(item.sentiment_score)}
                    >
                      {item.sentiment_score > 0 ? "+" : ""}
                      {item.sentiment_score} Sentiment
                    </Typography>
                  </Box>

                  {/* Top Headline & Volume */}
                  <Stack
                    direction="row"
                    alignItems="center"
                    justifyContent="space-between"
                    mt={2}
                  >
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <ArticleIcon fontSize="small" color="action" />
                      <Typography variant="caption" color="text.secondary">
                        {item.article_count} recent articles
                      </Typography>
                    </Box>
                  </Stack>

                  {/* FIX: Safe access using optional chaining */}
                  {item.top_articles && item.top_articles.length > 0 && (
                    <Box mt={1} p={1} bgcolor="#f5f5f5" borderRadius={1}>
                      <Typography
                        variant="caption"
                        fontStyle="italic"
                        color="text.primary"
                      >
                        "{item.top_articles[0].title}"
                      </Typography>
                      <Typography
                        variant="caption"
                        display="block"
                        color="text.secondary"
                        fontSize="0.7rem"
                      >
                        — {item.top_articles[0].source_name}
                      </Typography>
                    </Box>
                  )}
                </ListItem>
                {index < data.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
