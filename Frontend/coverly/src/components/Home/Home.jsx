import React from "react";
import { Sparkles } from "lucide-react";
import { useSelector } from "react-redux";
import DesignSettings from "./DesignSettings";
import Output from "./Output";
import "../../styles/home.css";
import ModeToggle from "../utilities/ModeToggle";

export default function Home() {
  const { isDarkMode } = useSelector((state) => state.home);

  const bgClass = isDarkMode ? "bg-black" : "bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50";
  const textPrimary = isDarkMode ? "text-white" : "text-gray-900";
  const textSecondary = isDarkMode ? "text-neutral-500" : "text-gray-600";

  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-500 pt-5 pb-10`}>
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12 px-4 sm:px-6 lg:px-0 animate-fadeIn">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 gap-4 sm:gap-0">
          {/* Logo + Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center shadow-lg animate-float">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className={`text-3xl font-bold ${textPrimary}`}>Coverly</h1>
          </div>

          <ModeToggle />
        </div>

        <p className={`${textSecondary} text-lg`}>Create stunning thumbnails in seconds with AI</p>
      </div>

      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-8">
        <DesignSettings />
        <Output />
      </div>
    </div>
  );
}
