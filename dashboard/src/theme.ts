import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#0f62fe" },
    secondary: { main: "#6f6f6f" },
    background: { default: "#f7f8fa", paper: "#ffffff" },
  },
  shape: { borderRadius: 14 },
});

export default theme;
