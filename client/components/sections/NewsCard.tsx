// client/components/sections/NewsCard.tsx
"use client";

import ArticleIcon from "@mui/icons-material/Article";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import ScoreIcon from "@mui/icons-material/Score";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  LinearProgress,
  List,
  ListItem,
  Stack,
  Typography,
} from "@mui/material";
import React from "react";

interface Props {
  shows: any[];
}

export default function NewsCard({ shows }: Props) {
  const validShows = shows.filter((s) => s.news && s.news.score !== undefined);

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
        subheader="Media Coverage & Scoring (15% Weight)"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        <List disablePadding>
          {validShows.map((show, index) => {
            const n = show.news;
            return (
              <React.Fragment key={show.show_name}>
                <ListItem sx={{ display: "block", py: 2 }}>
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
                      label={`Score: ${n.score}`}
                      size="small"
                      color={n.score > 60 ? "success" : "primary"}
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
                      // Normalize -1..1 to 0..100
                      value={((n.sentiment + 1) / 2) * 100}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: "#ffebee",
                        "& .MuiLinearProgress-bar": {
                          bgcolor: getSentimentColor(n.sentiment),
                        },
                      }}
                    />
                    <Typography
                      variant="caption"
                      display="block"
                      textAlign="center"
                      mt={0.5}
                      fontWeight="bold"
                      color={getSentimentColor(n.sentiment)}
                    >
                      {n.sentiment > 0 ? "+" : ""}
                      {n.sentiment} Sentiment
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
                        {n.article_count} recent articles
                      </Typography>
                    </Box>
                  </Stack>

                  {n.top_headline && (
                    <Box mt={1} p={1} bgcolor="#f5f5f5" borderRadius={1}>
                      <Typography
                        variant="caption"
                        fontStyle="italic"
                        color="text.primary"
                      >
                        "{n.top_headline}"
                      </Typography>
                    </Box>
                  )}
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
