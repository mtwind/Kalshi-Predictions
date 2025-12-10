// client/components/sections/YoutubeCard.tsx
"use client";

import EmojiEmotionsIcon from "@mui/icons-material/EmojiEmotions";
import RefreshIcon from "@mui/icons-material/Refresh";
import ScoreIcon from "@mui/icons-material/Score";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import VisibilityIcon from "@mui/icons-material/Visibility";
import YouTubeIcon from "@mui/icons-material/YouTube";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  List,
  ListItem,
  Stack,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";

import { fetchKalshiTop, fetchYoutubeAnalysis } from "../../services/api";
import { normalizeShowName } from "../../utils/formatters";

// Updated Interface based on new backend logic
interface YoutubeMetrics {
  show_name: string;
  total_views: number;
  total_likes: number;
  avg_like_percentage: number;
  sentiment_score: number;
  final_score: number;
}

interface Props {
  refreshTrigger: number;
}

export default function YoutubeCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("Initializing...");
  const [data, setData] = useState<YoutubeMetrics[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setLoadingStatus("Fetching shows...");
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
      const results: YoutubeMetrics[] = [];

      for (let i = 0; i < shows.length; i++) {
        const show = shows[i];
        setLoadingStatus(
          `Analyzing Top 10 Videos for ${show} (${i + 1}/${shows.length})...`
        );

        try {
          const analysis = await fetchYoutubeAnalysis(show);
          results.push(analysis);
        } catch (e) {
          console.warn(`Failed YouTube analysis for ${show}`, e);
        }
      }

      // Sort by Final Score (the new balanced metric)
      results.sort((a, b) => b.final_score - a.final_score);
      setData(results);
    } catch (err) {
      console.error("YouTube error", err);
      setError("Failed to load YouTube data");
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + "B";
    if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
    if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
    return num.toString();
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<YouTubeIcon sx={{ color: "#FF0000" }} />}
        title="YouTube Deep Dive"
        subheader="Top 10 Videos Analysis"
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
            <CircularProgress size={30} sx={{ color: "#FF0000" }} />
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
                  {/* Header: Title & Final Score */}
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
                      label={`Score: ${item.final_score}`}
                      size="small"
                      color={
                        item.final_score > 75
                          ? "success"
                          : item.final_score > 50
                          ? "primary"
                          : "default"
                      }
                      variant="filled"
                    />
                  </Box>

                  {/* Metrics Row */}
                  <Stack
                    direction="row"
                    divider={<Divider orientation="vertical" flexItem />}
                    spacing={2}
                    justifyContent="space-between"
                  >
                    {/* Views */}
                    <Box textAlign="center">
                      <Typography variant="caption" color="text.secondary">
                        Total Views
                      </Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <VisibilityIcon fontSize="inherit" color="action" />
                        <Typography variant="body2" fontWeight="bold">
                          {formatNumber(item.total_views)}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Like % */}
                    <Box textAlign="center">
                      <Typography variant="caption" color="text.secondary">
                        Like Ratio
                      </Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <ThumbUpIcon fontSize="inherit" color="action" />
                        <Typography variant="body2" fontWeight="bold">
                          {item.avg_like_percentage}%
                        </Typography>
                      </Box>
                    </Box>

                    {/* Sentiment */}
                    <Box textAlign="center">
                      <Typography variant="caption" color="text.secondary">
                        Sentiment
                      </Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <EmojiEmotionsIcon
                          fontSize="inherit"
                          color={
                            item.sentiment_score > 0.2
                              ? "success"
                              : item.sentiment_score < -0.2
                              ? "error"
                              : "action"
                          }
                        />
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          color={
                            item.sentiment_score > 0
                              ? "success.main"
                              : "text.primary"
                          }
                        >
                          {item.sentiment_score > 0 ? "+" : ""}
                          {item.sentiment_score}
                        </Typography>
                      </Box>
                    </Box>
                  </Stack>
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
