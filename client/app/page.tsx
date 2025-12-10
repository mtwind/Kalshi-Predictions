// client/app/page.tsx
"use client";

import MenuIcon from "@mui/icons-material/Menu";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  AppBar,
  Box,
  CircularProgress,
  Container,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";
import Grid from "@mui/material/Grid"; // or Grid2 if using MUI v6
import { useEffect, useState } from "react";

// Components
import KalshiCard from "@/components/sections/KalshiCard";
import NewsCard from "@/components/sections/NewsCard";
import TmdbCard from "@/components/sections/TmdbCard";
import WikipediaCard from "@/components/sections/WikipediaCard";
import YoutubeCard from "@/components/sections/YoutubeCard";

import { fetchLatestAnalysis, refreshAnalysis } from "../services/api";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Initial Load from the JSON Snapshot
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const json = await fetchLatestAnalysis();
      setData(json);
      if (json.timestamp) {
        setLastUpdated(new Date(json.timestamp).toLocaleTimeString());
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshAll = async () => {
    setRefreshing(true);
    try {
      const json = await refreshAnalysis();
      setData(json);
      if (json.timestamp) {
        setLastUpdated(new Date(json.timestamp).toLocaleTimeString());
      }
    } catch (err) {
      console.error(err);
      setError("Failed to refresh data.");
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: "#f5f5f5", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Prediction Market Dashboard
          </Typography>

          <Box mr={2}>
            {lastUpdated && (
              <Typography variant="caption" display="block" align="right">
                Updated: {lastUpdated}
              </Typography>
            )}
          </Box>

          <IconButton
            color="inherit"
            onClick={handleRefreshAll}
            disabled={refreshing}
          >
            {refreshing ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              <RefreshIcon />
            )}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" mt={10}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {/* Row 1: High Priority - Kalshi & Wikipedia */}
            <Grid item xs={12} md={6} lg={4}>
              <KalshiCard shows={data?.shows || []} />
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <WikipediaCard shows={data?.shows || []} />
            </Grid>
            <Grid item xs={12} md={12} lg={4}>
              <TmdbCard shows={data?.shows || []} />
            </Grid>

            {/* Row 2: Media & News */}
            <Grid item xs={12} md={6}>
              <YoutubeCard shows={data?.shows || []} />
            </Grid>
            <Grid item xs={12} md={6}>
              <NewsCard shows={data?.shows || []} />
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
}
