// client/components/sections/TmdbCard.tsx
"use client";

import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import MovieIcon from "@mui/icons-material/Movie";
import RefreshIcon from "@mui/icons-material/Refresh";
import ScoreIcon from "@mui/icons-material/Score";
import StarIcon from "@mui/icons-material/Star";
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

import { fetchKalshiTop, fetchTmdbAnalysis } from "../../services/api";
import { normalizeShowName } from "../../utils/formatters";

interface TmdbMetrics {
  name: string;
  found: boolean;
  tmdb_score: number;
  vote_average: number;
  vote_count: number;
  popularity: number;
  trending_rank: number | null;
}

interface Props {
  refreshTrigger: number;
}

export default function TmdbCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("Initializing...");
  const [data, setData] = useState<TmdbMetrics[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setLoadingStatus("Fetching market data...");
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
      const results: TmdbMetrics[] = [];

      for (let i = 0; i < shows.length; i++) {
        const show = shows[i];
        setLoadingStatus(
          `Analyzing TMDB for ${show} (${i + 1}/${shows.length})...`
        );

        try {
          const analysis = await fetchTmdbAnalysis(show);
          if (analysis.found) {
            results.push(analysis);
          }
        } catch (e) {
          console.warn(`Failed TMDB analysis for ${show}`, e);
        }
      }

      // Sort by the new TMDB Score
      results.sort((a, b) => b.tmdb_score - a.tmdb_score);
      setData(results);
    } catch (err) {
      console.error(err);
      setError("Failed to load TMDB metrics");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<MovieIcon sx={{ color: "#01B4E4" }} />}
        title="TV Popularity"
        subheader="TMDB Scores & Trends"
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
            <CircularProgress size={30} sx={{ color: "#01B4E4" }} />
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
              <React.Fragment key={item.name}>
                <ListItem sx={{ display: "block", py: 2 }}>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    mb={1.5}
                  >
                    <Typography variant="subtitle2" fontWeight="bold">
                      {item.name}
                    </Typography>

                    {/* Score Chip */}
                    <Chip
                      icon={<ScoreIcon />}
                      label={`Score: ${item.tmdb_score}`}
                      size="small"
                      color={item.tmdb_score > 80 ? "success" : "primary"}
                      variant="filled"
                    />
                  </Box>

                  <Stack direction="row" spacing={2} alignItems="center">
                    {/* Vote Average */}
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <StarIcon sx={{ color: "#FFC107", fontSize: 18 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {item.vote_average.toFixed(1)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ({item.vote_count})
                      </Typography>
                    </Box>

                    {/* Trending Badge (if applicable) */}
                    {item.trending_rank && (
                      <Chip
                        icon={<LocalFireDepartmentIcon fontSize="small" />}
                        label={`#${item.trending_rank} Trending`}
                        size="small"
                        color="warning"
                        variant="outlined"
                        sx={{ height: 24 }}
                      />
                    )}

                    {/* Raw Popularity (Backup) */}
                    {!item.trending_rank && (
                      <Typography variant="caption" color="text.secondary">
                        Pop: {item.popularity}
                      </Typography>
                    )}
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
