// client/components/sections/KalshiCard.tsx
"use client";

import TrendingUpIcon from "@mui/icons-material/TrendingUp";
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
  Tooltip,
  Typography,
} from "@mui/material";
import React from "react";

interface Props {
  shows: any[];
}

export default function KalshiCard({ shows }: Props) {
  // Filter for shows that actually have Kalshi data
  const validShows = shows.filter((s) => s.kalshi);

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<TrendingUpIcon color="primary" />}
        title="Kalshi Markets"
        subheader="Live Prediction Odds (50% Weight)"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto", p: 0 }}>
        <List disablePadding>
          {validShows.map((show, index) => {
            const m = show.kalshi;
            // Calculate chance (implied prob)
            const chance = m.chance || m.last_price || 0;

            return (
              <React.Fragment key={show.show_name}>
                <ListItem sx={{ display: "block", py: 2 }}>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    mb={1}
                  >
                    <Typography variant="subtitle2" fontWeight="bold">
                      {show.show_name}
                    </Typography>
                    <Chip
                      label={`${chance}%`}
                      color={chance > 50 ? "success" : "default"}
                      size="small"
                      sx={{ fontWeight: "bold" }}
                    />
                  </Box>

                  <Stack direction="row" spacing={1} mt={1}>
                    <Tooltip title={`Bid: ${m.yes_bid}¢ | Ask: ${m.yes_ask}¢`}>
                      <Chip
                        label={`Yes ${m.yes_ask}¢`}
                        size="small"
                        sx={{
                          bgcolor: "#e6f4ea",
                          color: "#137333",
                          fontWeight: "bold",
                          minWidth: 70,
                          cursor: "pointer",
                        }}
                      />
                    </Tooltip>

                    <Tooltip title={`Bid: ${m.no_bid}¢ | Ask: ${m.no_ask}¢`}>
                      <Chip
                        label={`No ${m.no_ask}¢`}
                        size="small"
                        sx={{
                          bgcolor: "#fce8e6",
                          color: "#d93025",
                          fontWeight: "bold",
                          minWidth: 70,
                          cursor: "pointer",
                        }}
                      />
                    </Tooltip>

                    <Typography
                      variant="caption"
                      sx={{
                        ml: "auto !important",
                        alignSelf: "center",
                        color: "text.secondary",
                      }}
                    >
                      Vol: {m.volume}
                    </Typography>
                  </Stack>
                </ListItem>
                {index < validShows.length - 1 && <Divider component="li" />}
              </React.Fragment>
            );
          })}

          {validShows.length === 0 && (
            <Box p={3} textAlign="center">
              <Typography variant="body2" color="text.secondary">
                No active markets found.
              </Typography>
            </Box>
          )}
        </List>
      </CardContent>
    </Card>
  );
}
