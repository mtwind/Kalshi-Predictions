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
  const getRecommendationColor = (rec: string) => {
    if (rec.includes("BUY YES")) return "success";
    if (rec.includes("BUY NO")) return "error"; // Using red for "Short/No" actions
    return "default";
  };

  const getRecommendationIcon = (rec: string) => {
    if (rec.includes("BUY YES")) return <TrendingUpIcon fontSize="small" />;
    if (rec.includes("BUY NO")) return <TrendingDownIcon fontSize="small" />;
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

                // Determine relevant market price
                // BUY YES -> We pay Ask Price
                // BUY NO  -> We effectively bet against Bid Price (Selling Yes)
                let marketPrice = 0;
                if (rec === "BUY YES") {
                  marketPrice = show.kalshi?.yes_ask;
                } else if (rec === "BUY NO") {
                  marketPrice = show.kalshi?.yes_bid;
                } else {
                  marketPrice = show.kalshi?.last_price;
                }

                return (
                  <TableRow key={show.show_name} hover>
                    <TableCell component="th" scope="row">
                      <Typography variant="body2" fontWeight="bold">
                        {show.show_name}
                      </Typography>
                    </TableCell>

                    <TableCell align="center">
                      <Typography variant="caption" fontWeight="bold">
                        {show.final_composite_score}
                      </Typography>
                    </TableCell>

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

                    <TableCell align="center">
                      <Typography variant="caption" color="text.secondary">
                        {marketPrice ? `${marketPrice}¢` : "-"}
                      </Typography>
                    </TableCell>

                    <TableCell align="center">
                      {edge > 0 && (
                        <Typography
                          variant="caption"
                          fontWeight="bold"
                          color={
                            rec === "BUY YES" ? "success.main" : "error.main"
                          }
                        >
                          {rec === "BUY YES" ? "+" : "-"}
                          {edge}
                        </Typography>
                      )}
                      {edge === 0 && (
                        <Typography variant="caption">-</Typography>
                      )}
                    </TableCell>

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
