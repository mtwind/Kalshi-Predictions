// client/components/sections/SummaryCard.tsx
"use client";

import MonetizationOnIcon from "@mui/icons-material/MonetizationOn";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

interface Props {
  shows: any[];
}

export default function SummaryCard({ shows }: Props) {
  // Shows are already sorted by Fair Price / Score from the backend

  const getRecommendationColor = (rec: string) => {
    if (rec.includes("BUY")) return "success";
    if (rec.includes("SELL")) return "error";
    return "default";
  };

  const getRecommendationIcon = (rec: string) => {
    if (rec.includes("BUY")) return <TrendingUpIcon fontSize="small" />;
    if (rec.includes("SELL")) return <TrendingDownIcon fontSize="small" />;
    return <TrendingFlatIcon fontSize="small" />;
  };

  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader
        avatar={<MonetizationOnIcon color="primary" />}
        title="Trade Opportunities"
        subheader="Fair Price vs. Market Reality"
      />
      <Divider />
      <CardContent sx={{ p: 0 }}>
        <TableContainer>
          <Table size="small">
            <TableHead sx={{ bgcolor: "#f5f5f5" }}>
              <TableRow>
                <TableCell>Show</TableCell>
                <TableCell align="center">Score</TableCell>
                <TableCell align="center">Fair Price</TableCell>
                <TableCell align="center">Mkt Price</TableCell>
                <TableCell align="center">Edge</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {shows.map((show) => {
                const rec = show.recommendation || "HOLD";
                const edge = show.edge_points || 0;

                // Determine which market price is relevant
                const isBuy = rec.includes("BUY");
                const marketPrice = isBuy
                  ? show.kalshi?.yes_ask
                  : show.kalshi?.yes_bid;

                return (
                  <TableRow key={show.show_name} hover>
                    <TableCell component="th" scope="row">
                      <Typography variant="body2" fontWeight="bold">
                        {show.show_name}
                      </Typography>
                    </TableCell>

                    {/* Final Composite Score */}
                    <TableCell align="center">
                      <Typography variant="caption" fontWeight="bold">
                        {show.final_composite_score}
                      </Typography>
                    </TableCell>

                    {/* Calculated Fair Price */}
                    <TableCell align="center">
                      <Box
                        sx={{
                          display: "inline-block",
                          bgcolor: "#e3f2fd",
                          color: "#1565c0",
                          px: 1,
                          borderRadius: 1,
                          fontSize: "0.8rem",
                          fontWeight: "bold",
                        }}
                      >
                        {show.fair_price}¢
                      </Box>
                    </TableCell>

                    {/* Market Price (Ask if Buy, Bid if Sell) */}
                    <TableCell align="center">
                      <Typography variant="caption" color="text.secondary">
                        {marketPrice ? `${marketPrice}¢` : "-"}
                      </Typography>
                    </TableCell>

                    {/* Edge Points */}
                    <TableCell align="center">
                      {edge > 0 && (
                        <Typography
                          variant="caption"
                          fontWeight="bold"
                          color={isBuy ? "success.main" : "error.main"}
                        >
                          {isBuy ? "+" : "-"}
                          {edge}
                        </Typography>
                      )}
                      {edge === 0 && (
                        <Typography variant="caption">-</Typography>
                      )}
                    </TableCell>

                    {/* Action Chip */}
                    <TableCell align="right">
                      <Chip
                        icon={getRecommendationIcon(rec)}
                        label={rec}
                        size="small"
                        color={getRecommendationColor(rec) as any}
                        variant={rec === "HOLD" ? "outlined" : "filled"}
                        sx={{ fontWeight: "bold", minWidth: 85 }}
                      />
                    </TableCell>
                  </TableRow>
                );
              })}

              {shows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                    <Typography variant="caption" color="text.secondary">
                      No analysis data available.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
