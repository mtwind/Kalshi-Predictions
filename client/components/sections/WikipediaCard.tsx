// client/components/sections/WikipediaCard.tsx
"use client";

import LanguageIcon from "@mui/icons-material/Language";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Divider,
  LinearProgress,
  List,
  ListItem,
  Typography,
} from "@mui/material";
import React from "react";

interface Props {
  shows: any[];
}

export default function WikipediaCard({ shows }: Props) {
  // Filter for shows that have a wikipedia object
  const validShows = shows.filter((s) => s.wikipedia);

  // Find max views safely (default to 1 to avoid division by zero)
  const maxViews = Math.max(
    ...validShows.map((s) => s.wikipedia.total_weekly_views || 0),
    1
  );

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<LanguageIcon color="secondary" />}
        title="Wikipedia Traffic"
        subheader="7-Day Pageview Volume (5% Weight)"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        <List disablePadding>
          {validShows.map((show, index) => {
            const w = show.wikipedia;
            // FIX: Use null coalescing (?? 0) to prevent crashes if fields are undefined
            const totalViews = w?.total_weekly_views ?? 0;
            const dailyAvg = w?.avg_daily_views ?? 0;

            return (
              <React.Fragment key={show.show_name}>
                <ListItem sx={{ display: "block", py: 1.5 }}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {show.show_name}
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color="primary"
                    >
                      {/* FIX: formatting safe value */}
                      {totalViews.toLocaleString()}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(totalViews / maxViews) * 100}
                    sx={{ height: 8, borderRadius: 1, bgcolor: "#f0f0f0" }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: "block" }}
                  >
                    {/* FIX: formatting safe value */}~
                    {dailyAvg.toLocaleString()} / day
                  </Typography>
                </ListItem>
                {index < validShows.length - 1 && <Divider />}
              </React.Fragment>
            );
          })}

          {validShows.length === 0 && (
            <Box p={2} textAlign="center">
              <Typography variant="caption" color="text.secondary">
                No Wikipedia data available.
              </Typography>
            </Box>
          )}
        </List>
      </CardContent>
    </Card>
  );
}
