// client/components/sections/YoutubeCard.tsx
"use client";

import EmojiEmotionsIcon from "@mui/icons-material/EmojiEmotions";
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
  Divider,
  List,
  ListItem,
  Stack,
  Typography,
} from "@mui/material";
import React from "react";

interface Props {
  shows: any[];
}

export default function YoutubeCard({ shows }: Props) {
  const validShows = shows.filter((s) => s.youtube && s.youtube.totals);

  const formatNumber = (num: number) => {
    if (!num) return "0";
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
        subheader="Top 10 Videos Analysis (20% Weight)"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        <List disablePadding>
          {validShows.map((show, index) => {
            const yt = show.youtube;
            const stats = yt.totals; // Access the pre-calculated totals

            return (
              <React.Fragment key={show.show_name}>
                <ListItem sx={{ display: "block", py: 2 }}>
                  {/* Header: Title & Final Score */}
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    mb={1.5}
                  >
                    <Typography variant="subtitle2" fontWeight="bold">
                      {show.show_name}
                    </Typography>
                    <Chip
                      icon={<ScoreIcon />}
                      label={`Score: ${stats.youtube_score}`}
                      size="small"
                      color={
                        stats.youtube_score > 75
                          ? "success"
                          : stats.youtube_score > 50
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
                        Avg Views
                      </Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <VisibilityIcon fontSize="inherit" color="action" />
                        <Typography variant="body2" fontWeight="bold">
                          {formatNumber(stats.average_views)}
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
                          {stats.like_percentage}%
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
                            stats.sentiment_average > 0.2
                              ? "success"
                              : stats.sentiment_average < -0.2
                              ? "error"
                              : "action"
                          }
                        />
                        <Typography
                          variant="body2"
                          fontWeight="bold"
                          color={
                            stats.sentiment_average > 0
                              ? "success.main"
                              : "text.primary"
                          }
                        >
                          {stats.sentiment_average > 0 ? "+" : ""}
                          {stats.sentiment_average}
                        </Typography>
                      </Box>
                    </Box>
                  </Stack>
                </ListItem>
                {index < validShows.length - 1 && <Divider component="li" />}
              </React.Fragment>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
}
