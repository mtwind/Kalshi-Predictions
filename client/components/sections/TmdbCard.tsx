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
  const validShows = shows.filter((s) => s.tmdb && s.tmdb.score !== undefined);

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
                      label={`Score: ${t.score}`}
                      size="small"
                      color={t.score > 80 ? "success" : "primary"}
                      variant="filled"
                    />
                  </Box>

                  <Stack direction="row" spacing={2} alignItems="center">
                    {/* Vote Average */}
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <StarIcon sx={{ color: "#FFC107", fontSize: 18 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {t.rating?.toFixed(1)}
                      </Typography>
                    </Box>

                    {/* Popularity */}
                    <Typography variant="caption" color="text.secondary">
                      Pop: {t.popularity}
                    </Typography>
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
