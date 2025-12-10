// client/app/page.tsx
"use client";

import {
  AppBar,
  Box,
  Container,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";
import { useState } from "react";
// Import Grid2 (the new standard in MUI v6)
import MenuIcon from "@mui/icons-material/Menu";
import RefreshIcon from "@mui/icons-material/Refresh";
import Grid from "@mui/material/Grid";

import KalshiCard from "../components/sections/KalshiCard";
import TmdbCard from "../components/sections/TmdbCard";
import WikipediaCard from "../components/sections/WikipediaCard";
import YoutubeCard from "../components/sections/YoutubeCard";

export default function Dashboard() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleRefreshAll = () => {
    setRefreshTrigger((prev) => prev + 1);
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
          <IconButton color="inherit" onClick={handleRefreshAll}>
            <RefreshIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Grid v2 Container */}
        <Grid container spacing={3}>
          {/* Row 1: High Priority */}
          <Grid size={{ xs: 12, md: 6, lg: 4 }}>
            <KalshiCard refreshTrigger={refreshTrigger} />
          </Grid>
          {/* <Grid size={{ xs: 12, md: 6, lg: 4 }}>
            <TrendsCard refreshTrigger={refreshTrigger} />
          </Grid> */}
          <Grid size={{ xs: 12, md: 12, lg: 4 }}>
            <WikipediaCard refreshTrigger={refreshTrigger} />
          </Grid>

          {/* Row 2: Media */}
          <Grid size={{ xs: 12, md: 6 }}>
            <YoutubeCard refreshTrigger={refreshTrigger} />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <TmdbCard refreshTrigger={refreshTrigger} />
          </Grid>

          {/* Row 3: News */}
          {/* <Grid size={{ xs: 12 }}>
            <NewsCard refreshTrigger={refreshTrigger} />
          </Grid> */}
        </Grid>
      </Container>
    </Box>
  );
}

// Good. Now, i want to change things up so that all data is fetched by a single function, including kalshi markets, news data, wikipedia data, tmdb data, and youtube data. I have decided to exclude trend data sinc ethe api is not reliable. Can you build a backend function that does ALL of this? Basically, it should simulate reloading the page, so all data is fetched. Then, store this data in data/full-analysis. I have attached all relevant files for reference on strategy of data collection
