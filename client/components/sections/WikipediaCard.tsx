"use client";

import LanguageIcon from "@mui/icons-material/Language";
import RefreshIcon from "@mui/icons-material/Refresh";
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
import { fetchKalshiTop, fetchWikiPageviews } from "../../services/api";
import { formatDate, normalizeShowName } from "../../utils/formatters";

interface WikiData {
  article: string;
  total_views: number;
  daily_avg: number;
}

interface Props {
  refreshTrigger: number;
}

export default function WikipediaCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<WikiData[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const kalshiData = await fetchKalshiTop(5);
      if (!kalshiData.markets) throw new Error("No markets found");

      const uniqueShows = new Set<string>();
      kalshiData.markets.forEach((m: any) => {
        const rawName = m.subtitle || m.title || "";
        const cleanName = normalizeShowName(rawName);
        if (cleanName) uniqueShows.add(cleanName);
      });

      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 10);

      const requests = Array.from(uniqueShows).map(async (show) => {
        try {
          // Wiki API expects underscores
          const apiName = show.replace(/\s+/g, "_");
          const res = await fetchWikiPageviews(
            apiName,
            formatDate(start),
            formatDate(end)
          );

          const totalViews = res.points
            ? res.points.reduce((acc: number, day: any) => acc + day.views, 0)
            : 0;

          return {
            article: show, // Keep spaces for display
            total_views: totalViews,
            daily_avg: Math.round(totalViews / 10),
          };
        } catch (e) {
          console.warn(`Failed to fetch wiki for ${show}`, e);
          return null;
        }
      });

      const results = await Promise.all(requests);
      const validResults = results
        .filter((r): r is WikiData => r !== null)
        .sort((a, b) => b.total_views - a.total_views);

      setData(validResults);
    } catch (err) {
      console.error("Failed to fetch Wikipedia data", err);
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const maxViews = data.length > 0 ? data[0].total_views : 1;

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<LanguageIcon color="primary" />}
        title="Wikipedia Interest"
        subheader="Pageviews (Last 10 Days)"
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
        ) : (
          <List disablePadding>
            {data.map((item, index) => (
              <React.Fragment key={item.article}>
                <ListItem sx={{ display: "block", py: 1.5 }}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {item.article}
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color="primary"
                    >
                      {item.total_views.toLocaleString()}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(item.total_views / maxViews) * 100}
                    sx={{ height: 8, borderRadius: 1, bgcolor: "#f0f0f0" }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: "block" }}
                  >
                    ~{item.daily_avg.toLocaleString()} / day
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
