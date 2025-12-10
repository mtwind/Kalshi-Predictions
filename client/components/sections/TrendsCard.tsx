// client/components/sections/KalshiCard.tsx
"use client";

import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  CircularProgress,
  Divider,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

interface Props {
  refreshTrigger: number;
}

export default function TrendsCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchData();
  }, [refreshTrigger]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // TODO: Replace with real fetch to your FastAPI server
      // const res = await fetch('http://localhost:8000/kalshi/netflix/top');
      // const json = await res.json();

      // Simulating delay for now
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setData({ status: "Connected", markets: 5 });
    } catch (error) {
      console.error("Failed to fetch Kalshi data", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<TrendingUpIcon color="primary" />}
        title="Kalshi Markets"
        subheader="Live Prediction Odds"
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1 }}>
        {loading ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="100%"
          >
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            <Typography variant="body1">
              Placeholder for Kalshi Data Grid.
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date().toLocaleTimeString()}
            </Typography>
            {/* Here we will map over `data.markets` and display them.
             */}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
