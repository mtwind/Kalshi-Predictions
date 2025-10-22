import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import LaunchIcon from "@mui/icons-material/Launch";
import RadioButtonUncheckedIcon from "@mui/icons-material/RadioButtonUnchecked";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Stack,
  Typography,
} from "@mui/material";

type Props = {
  name: string;
  category: string;
  desc: string;
  docsUrl?: string;
  connected?: boolean;
  onConnect?: () => void;
  onView?: () => void;
};

export default function DataCard({
  name,
  category,
  desc,
  docsUrl,
  connected,
  onConnect,
  onView,
}: Props) {
  return (
    <Card
      elevation={1}
      sx={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={1}
        >
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {name}
          </Typography>
          <Chip
            label={category}
            size="small"
            color={category === "Social" ? "secondary" : "primary"}
            variant="outlined"
          />
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center" mb={1}>
          {connected ? (
            <CheckCircleIcon fontSize="small" />
          ) : (
            <RadioButtonUncheckedIcon fontSize="small" />
          )}
          <Typography variant="caption" color="text.secondary">
            {connected ? "Connected" : "Not connected"}
          </Typography>
        </Stack>

        <Typography variant="body2" color="text.secondary">
          {desc}
        </Typography>
      </CardContent>

      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button size="small" variant="contained" onClick={onView}>
          View
        </Button>
        <Button size="small" variant="outlined" onClick={onConnect}>
          {connected ? "Manage" : "Connect"}
        </Button>
        {docsUrl && (
          <Button
            size="small"
            endIcon={<LaunchIcon />}
            onClick={() => window.open(docsUrl, "_blank")}
          >
            Docs
          </Button>
        )}
      </CardActions>
    </Card>
  );
}
