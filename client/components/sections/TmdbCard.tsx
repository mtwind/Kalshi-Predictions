// client/components/sections/TmdbCard.tsx
"use client";

import MovieIcon from "@mui/icons-material/Movie";
import ScoreIcon from "@mui/icons-material/Score";
import StarIcon from "@mui/icons-material/Star";
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

export default function TmdbCard({ shows }: Props) {
  // FIX: Filter using 'tmdb_score' instead of 'score'
  const validShows = shows.filter(
    (s) => s.tmdb && s.tmdb.tmdb_score !== undefined
  );

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<MovieIcon sx={{ color: "#01B4E4" }} />}
        title="TV Popularity"
        subheader="TMDB Ratings & Trends (10% Weight)"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        <List disablePadding>
          {validShows.map((show, index) => {
            const t = show.tmdb;
            const rating = t.vote_average ?? 0;
            const popularity = t.popularity ?? 0;
            // FIX: Read 'tmdb_score'
            const score = t.tmdb_score ?? 0;

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
                      label={`Score: ${score}`}
                      size="small"
                      color={score > 80 ? "success" : "primary"}
                      variant="filled"
                    />
                  </Box>

                  <Stack direction="row" spacing={2} alignItems="center">
                    {/* Vote Average */}
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <StarIcon sx={{ color: "#FFC107", fontSize: 18 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {rating.toFixed(1)}
                      </Typography>
                      {/* Optional: Add vote count if available in your JSON */}
                      {t.vote_count > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          ({t.vote_count})
                        </Typography>
                      )}
                    </Box>

                    {/* Popularity */}
                    <Typography variant="caption" color="text.secondary">
                      Pop: {Math.round(popularity)}
                    </Typography>

                    {/* Trending Rank (Optional) */}
                    {t.trending_rank && (
                      <Chip
                        label={`#${t.trending_rank} Trending`}
                        size="small"
                        color="warning"
                        variant="outlined"
                        sx={{ height: 20, fontSize: "0.65rem" }}
                      />
                    )}
                  </Stack>
                </ListItem>
                {index < validShows.length - 1 && <Divider component="li" />}
              </React.Fragment>
            );
          })}

          {validShows.length === 0 && (
            <Box p={3} textAlign="center">
              <Typography variant="caption" color="text.secondary">
                No TMDB data available.
              </Typography>
            </Box>
          )}
        </List>
      </CardContent>
    </Card>
  );
}
