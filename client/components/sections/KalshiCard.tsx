"use client";

import RefreshIcon from "@mui/icons-material/Refresh";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
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
  ListItemText,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { fetchKalshiTop } from "../../services/api";

interface Market {
  ticker: string;
  title: string;
  subtitle?: string; // New field for clean names
  chance: number; // New field for probability
  yes_bid: number;
  yes_ask: number;
  no_bid: number;
  no_ask: number;
  last_price: number;
  volume: number;
}

interface KalshiData {
  markets: Market[];
}

interface Props {
  refreshTrigger: number;
}

export default function KalshiCard({ refreshTrigger }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<KalshiData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchKalshiTop(5);
      setData(result);
    } catch (err) {
      console.error("Failed to fetch Kalshi data", err);
      setError("Failed to load markets");
    } finally {
      setLoading(false);
    }
  };

  // Helper to fallback if subtitle is missing
  const getMarketName = (market: Market) => {
    if (market.subtitle) return market.subtitle;
    if (market.title.length < 30) return market.title;
    const parts = market.ticker.split("-");
    return parts[parts.length - 1] || market.ticker;
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<ShowChartIcon color="primary" />}
        title="Kalshi Markets"
        subheader="Netflix 2025 Rankings (Chance %)"
        action={
          <IconButton onClick={loadData} disabled={loading} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
        }
      />
      <Divider />
      <CardContent sx={{ flexGrow: 1, p: 0 }}>
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
            {data?.markets.map((market, index) => (
              <React.Fragment key={market.ticker}>
                <ListItem
                  sx={{
                    display: "flex",
                    flexDirection: { xs: "column", sm: "row" },
                    alignItems: { xs: "flex-start", sm: "center" },
                    gap: 2,
                    py: 1.5,
                  }}
                >
                  {/* Left: Chance Indicator */}
                  <Box sx={{ minWidth: 60, textAlign: "center" }}>
                    <Typography
                      variant="h6"
                      color="primary.main"
                      fontWeight="bold"
                    >
                      {market.chance}%
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ fontSize: "0.65rem" }}
                    >
                      CHANCE
                    </Typography>
                  </Box>

                  {/* Center: Market Name & Volume */}
                  <ListItemText
                    primary={
                      <Typography variant="subtitle1" fontWeight="500" noWrap>
                        {getMarketName(market)}
                      </Typography>
                    }
                    secondary={
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        component="span"
                      >
                        <TrendingUpIcon
                          sx={{ fontSize: 14, color: "text.secondary" }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          Vol: {market.volume.toLocaleString()}
                        </Typography>
                      </Stack>
                    }
                    sx={{ width: "100%", flex: 1 }}
                  />

                  {/* Right: Buy Prices (Ask) */}
                  <Stack direction="row" spacing={1}>
                    <Tooltip
                      title={`Spread: ${market.yes_bid}¢ - ${market.yes_ask}¢`}
                    >
                      <Chip
                        label={`Yes ${market.yes_ask}¢`}
                        size="small"
                        sx={{
                          bgcolor: "#e6f4ea",
                          color: "#1e8e3e",
                          fontWeight: "bold",
                          minWidth: 70,
                          borderRadius: 1,
                          cursor: "pointer",
                        }}
                      />
                    </Tooltip>

                    <Tooltip
                      title={`Spread: ${market.no_bid}¢ - ${market.no_ask}¢`}
                    >
                      <Chip
                        label={`No ${market.no_ask}¢`}
                        size="small"
                        sx={{
                          bgcolor: "#fce8e6",
                          color: "#d93025",
                          fontWeight: "bold",
                          minWidth: 70,
                          borderRadius: 1,
                          cursor: "pointer",
                        }}
                      />
                    </Tooltip>
                  </Stack>
                </ListItem>
                {index < (data?.markets.length || 0) - 1 && (
                  <Divider component="li" />
                )}
              </React.Fragment>
            ))}

            {(!data?.markets || data.markets.length === 0) && (
              <Box p={3} textAlign="center">
                <Typography variant="body2" color="text.secondary">
                  No active markets found.
                </Typography>
              </Box>
            )}
          </List>
        )}
      </CardContent>
    </Card>
  );
}
