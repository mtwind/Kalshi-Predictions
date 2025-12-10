"use client";

import RefreshIcon from "@mui/icons-material/Refresh";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  CircularProgress,
  Divider,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { fetchKalshiTop, fetchTrendsCompare } from "../../services/api";
import { formatDate, normalizeShowName } from "../../utils/formatters";

interface TrendSeries {
  date: string;
  value: number;
}

interface TrendData {
  term: string;
  points: TrendSeries[];
  currentValue: number;
  averageValue: number;
}

interface Props {
  refreshTrigger: number;
}

export default function TrendsCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<TrendData[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get Top Markets
      const kalshiData = await fetchKalshiTop(5);
      if (!kalshiData.markets) throw new Error("No markets found");

      const uniqueShows = new Set<string>();
      kalshiData.markets.forEach((m: any) => {
        const cleanName = normalizeShowName(m.subtitle || m.title || "");
        if (cleanName) uniqueShows.add(cleanName);
      });
      const shows = Array.from(uniqueShows);

      // 2. Define Date Range (Last 30 Days for trends)
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 30);

      // 3. Fetch Comparison Data (Single API Call)
      const res = await fetchTrendsCompare(
        shows,
        formatDate(start),
        formatDate(end)
      );

      if (!res.series) throw new Error("No trend data returned");

      // 4. Process Data
      const processed: TrendData[] = Object.keys(res.series).map((term) => {
        const points = res.series[term] || [];
        const values = points.map((p: any) => p.value);
        const current = values.length > 0 ? values[values.length - 1] : 0;
        const avg =
          values.reduce((a: number, b: number) => a + b, 0) /
          (values.length || 1);

        return {
          term,
          points,
          currentValue: current,
          averageValue: Math.round(avg),
        };
      });

      // Sort by current popularity
      processed.sort((a, b) => b.currentValue - a.currentValue);
      setData(processed);
    } catch (err) {
      console.error("Trends failed", err);
      setError("Failed to load trends");
    } finally {
      setLoading(false);
    }
  };

  // Find max value across all series to scale the bars
  const maxValue =
    data.reduce((max, item) => Math.max(max, item.currentValue), 0) || 100;

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<TrendingUpIcon color="primary" />}
        title="Google Search Trends"
        subheader="Relative Interest (Last 30 Days)"
        action={
          <IconButton onClick={loadData} disabled={loading} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
        }
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, overflowY: "auto" }}>
        {loading ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height={200}
          >
            <CircularProgress size={30} />
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
              No trend data available.
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {data.map((item, index) => (
              <React.Fragment key={item.term}>
                <ListItem sx={{ display: "block", py: 2 }}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {item.term}
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color="primary"
                    >
                      {item.currentValue}
                    </Typography>
                  </Box>

                  {/* Progress Bar showing current interest level */}
                  <LinearProgress
                    variant="determinate"
                    value={(item.currentValue / maxValue) * 100}
                    sx={{ height: 8, borderRadius: 1, mb: 1 }}
                  />

                  {/* Mini Sparkline Visualization (Simple SVG) */}
                  <Box height={24} width="100%" sx={{ opacity: 0.6 }}>
                    <svg width="100%" height="100%" preserveAspectRatio="none">
                      <polyline
                        fill="none"
                        stroke="#1976d2"
                        strokeWidth="2"
                        points={item.points
                          .map((p, i) => {
                            const x = (i / (item.points.length - 1)) * 100;
                            const y =
                              100 -
                              (p.value /
                                (Math.max(
                                  ...item.points.map((pt) => pt.value)
                                ) || 100)) *
                                100;
                            return `${x},${y}`;
                          })
                          .join(" ")}
                        vectorEffect="non-scaling-stroke" // Keeps line thickness constant
                      />
                    </svg>
                  </Box>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                    textAlign="right"
                  >
                    30-Day Trend
                  </Typography>
                </ListItem>
                {index < data.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
