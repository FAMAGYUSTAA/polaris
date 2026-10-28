import React from "react";

export default function HeroBanner({ stationId }) {
  const getStationDetails = (id) => {
    switch (id) {
      case "BHARATI":
        return "BHARATI STATION";
      case "MAITRI":
        return "MAITRI STATION";
      case "HIMADRI":
        return "HIMADRI STATION";
      default:
        return "UNKNOWN STATION";
    }
  };

  return (
    <div className="hero-banner">
      <div className="hero-overlay"></div>
      <div className="hero-content">
        <h1 className="hero-title">Polar Expedition Logistics</h1>
        <div className="hero-subtitle">
          {getStationDetails(stationId)}
        </div>
      </div>
    </div>
  );
}
