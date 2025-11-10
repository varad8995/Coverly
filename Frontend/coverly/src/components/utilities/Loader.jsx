import React from "react";
import LinearProgress from "@mui/material/LinearProgress";
import { useSelector } from "react-redux";

export default function Loader() {
  const { loading } = useSelector((state) => state.home);

  return (
    loading && (
      <div className="fixed top-0 left-0 right-0 z-50">
        <LinearProgress color="secondary" />
      </div>
    )
  );
}
