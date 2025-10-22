import { Box, Container, Tab, Tabs, Typography, useTheme } from "@mui/material";
import { useState } from "react";
import DataCard from "./components/DataCard";
import { DATA_SOURCES, type DataSource } from "./dataSources";

type Filter = "All" | "Popularity/Streaming" | "Social" | "Search";

function filterSources(s: DataSource[], f: Filter) {
  if (f === "All") return s;
  return s.filter((ds) => ds.category === f);
}

export default function App() {
  const theme = useTheme();
  const [filter, setFilter] = useState<Filter>("All");
  const [sources, setSources] = useState<DataSource[]>(DATA_SOURCES);

  const handleConnect = (key: DataSource["key"]) => {
    setSources((prev) =>
      prev.map((s) => (s.key === key ? { ...s, connected: !s.connected } : s))
    );
  };

  return (
    <Box sx={{ py: 4, backgroundColor: theme.palette.background.default }}>
      <Container maxWidth="lg">
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
          Alt-Data Sources
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Connect data feeds used to forecast Netflix weekly rankings.
        </Typography>

        <Tabs
          value={filter}
          onChange={(_, v) => setFilter(v)}
          sx={{ mb: 3 }}
          variant="scrollable"
          scrollButtons="auto"
        >
          {["All", "Popularity/Streaming", "Social", "Search"].map((label) => (
            <Tab key={label} value={label} label={label} />
          ))}
        </Tabs>

        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "flex-start",
            gap: 24,
          }}
        >
          {filterSources(sources, filter).map((src) => (
            <Box
              key={src.key}
              sx={{
                flex: "1 1 280px",
                maxWidth: "360px",
                minWidth: "260px",
              }}
            >
              <DataCard
                name={src.name}
                category={src.category}
                desc={src.desc}
                docsUrl={src.docsUrl}
                connected={src.connected}
                onConnect={() => handleConnect(src.key)}
                onView={() => alert(`Open ${src.name} details`)}
              />
            </Box>
          ))}
        </Box>
      </Container>
    </Box>
  );
}
