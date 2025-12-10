"use client";

import NewspaperIcon from "@mui/icons-material/Newspaper";
import RefreshIcon from "@mui/icons-material/Refresh";
import SentimentDissatisfiedIcon from "@mui/icons-material/SentimentDissatisfied";
import SentimentNeutralIcon from "@mui/icons-material/SentimentNeutral";
import SentimentSatisfiedAltIcon from "@mui/icons-material/SentimentSatisfiedAlt";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  Tooltip,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";

import { fetchGoogleNews, fetchKalshiTop } from "../../services/api";
import { formatDate, normalizeShowName } from "../../utils/formatters";

interface ShowSentiment {
  name: string;
  score: number;
  articleCount: number;
}

interface Props {
  refreshTrigger: number;
}

export default function NewsCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("Initializing...");
  const [data, setData] = useState<ShowSentiment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyzeSentiment();
  }, [refreshTrigger]);

  const analyzeSentiment = async () => {
    setLoading(true);
    setLoadingStatus("Fetching top markets...");
    setError(null);
    setData([]);

    try {
      const kalshiData = await fetchKalshiTop(5);
      if (!kalshiData.markets) throw new Error("No markets found");

      const uniqueShows = new Set<string>();
      kalshiData.markets.forEach((m: any) => {
        const rawName = m.subtitle || m.title || "";
        const cleanName = normalizeShowName(rawName);
        if (cleanName) uniqueShows.add(cleanName);
      });

      const shows = Array.from(uniqueShows);
      const results: ShowSentiment[] = [];

      // UPDATED: Extended window to 30 days for more results
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 30);
      const fromDate = formatDate(start);
      const toDate = formatDate(end);

      for (let i = 0; i < shows.length; i++) {
        const show = shows[i];
        setLoadingStatus(
          `Analyzing sentiment for ${show} (${i + 1}/${shows.length})...`
        );

        try {
          // UPDATED: Removed "Netflix" to broaden search results
          // We rely on the show name being unique enough (e.g. "Stranger Things")
          const query = `"${show}"`;
          const res = await fetchGoogleNews(query, fromDate, toDate);

          results.push({
            name: show,
            score: res.average_sentiment || 0,
            articleCount: res.count || 0,
          });
        } catch (e) {
          console.warn(`Failed to analyze news for ${show}`, e);
        }
      }

      results.sort((a, b) => b.score - a.score);
      setData(results);
    } catch (err) {
      console.error("News analysis failed", err);
      setError("Failed to analyze sentiment");
    } finally {
      setLoading(false);
    }
  };

  const getSentimentInfo = (score: number) => {
    if (score >= 0.05)
      return {
        color: "success.main",
        label: "Positive",
        Icon: SentimentSatisfiedAltIcon,
      };
    if (score <= -0.05)
      return {
        color: "error.main",
        label: "Negative",
        Icon: SentimentDissatisfiedIcon,
      };
    return {
      color: "text.secondary",
      label: "Neutral",
      Icon: SentimentNeutralIcon,
    };
  };

  const normalizeScoreToPercent = (score: number) => ((score + 1) / 2) * 100;

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<NewspaperIcon color="primary" />}
        title="News Sentiment"
        subheader="Analysis (Last 30 Days)"
        action={
          <IconButton
            onClick={analyzeSentiment}
            disabled={loading}
            size="small"
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        }
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto" }}>
        {loading ? (
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="center"
            alignItems="center"
            height={200}
            gap={2}
            p={3}
          >
            <LinearProgress sx={{ width: "100%", mb: 1 }} />
            <Typography variant="body2" color="text.secondary" align="center">
              {loadingStatus}
            </Typography>
          </Box>
        ) : error ? (
          <Box p={2} textAlign="center">
            <Typography color="error" variant="body2">
              {error}
            </Typography>
          </Box>
        ) : data.length === 0 ? (
          <Box p={3} textAlign="center">
            <Typography variant="body2" color="text.secondary">
              No news data available.
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {data.map((item, index) => {
              const { color, label, Icon } = getSentimentInfo(item.score);
              return (
                <React.Fragment key={item.name}>
                  <ListItem sx={{ display: "block", py: 1.5 }}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={1}
                    >
                      <Typography variant="subtitle2" fontWeight="bold">
                        {item.name}
                      </Typography>

                      <Tooltip title={`${label} (${item.score.toFixed(3)})`}>
                        <Chip
                          icon={<Icon style={{ fontSize: 16 }} />}
                          label={
                            item.score > 0
                              ? `+${item.score.toFixed(2)}`
                              : item.score.toFixed(2)
                          }
                          size="small"
                          variant="outlined"
                          sx={{
                            color: color,
                            borderColor: color,
                            fontWeight: "bold",
                            height: 24,
                          }}
                        />
                      </Tooltip>
                    </Box>

                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography
                        variant="caption"
                        color="error.main"
                        fontWeight="bold"
                      >
                        -1
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={normalizeScoreToPercent(item.score)}
                        sx={{
                          flexGrow: 1,
                          height: 8,
                          borderRadius: 1,
                          bgcolor: "#f0f0f0",
                          "& .MuiLinearProgress-bar": {
                            bgcolor: color,
                          },
                        }}
                      />
                      <Typography
                        variant="caption"
                        color="success.main"
                        fontWeight="bold"
                      >
                        +1
                      </Typography>
                    </Box>

                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 0.5, display: "block", textAlign: "right" }}
                    >
                      Based on {item.articleCount} articles
                    </Typography>
                  </ListItem>
                  {index < data.length - 1 && <Divider />}
                </React.Fragment>
              );
            })}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
