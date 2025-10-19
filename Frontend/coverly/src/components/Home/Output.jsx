import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { Sparkles, Download, RefreshCw, Image } from "lucide-react";
import { resetGeneration } from "../../redux/homeSlice";
import "../../styles/animations.css";

export default function Output() {
  const dispatch = useDispatch();
  const { isGenerating, hasGenerated, isDarkMode } = useSelector((state) => state.home);

  const cardBg = isDarkMode ? "bg-neutral-950 backdrop-blur-xl border-neutral-900" : "bg-white/80 backdrop-blur-xl border-purple-200/50";
  const textPrimary = isDarkMode ? "text-white" : "text-gray-900";
  const textSecondary = isDarkMode ? "text-neutral-500" : "text-gray-600";
  const inputBg = isDarkMode ? "bg-black border-neutral-900 text-white" : "bg-white border-purple-200 text-gray-900";

  const handleRegenerate = () => {
    dispatch(resetGeneration());
  };

  return (
    <div className={`${cardBg} border rounded-3xl p-8 shadow-xl transition-all duration-500 animate-slideInRight right-output-section`}>
      <h2 className={`text-xl font-semibold ${textPrimary} mb-6 flex items-center gap-2`}>
        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse"></div>
        Your Thumbnail
      </h2>

      {/* Output Area */}
      <div className="relative">
        {!hasGenerated && !isGenerating && (
          <div className={`aspect-video rounded-2xl ${inputBg} border-2 border-dashed flex items-center justify-center`}>
            <div className="text-center">
              <Image className={`w-16 h-16 mx-auto mb-4 ${textSecondary} opacity-40`} />
              <p className={`${textSecondary} text-sm`}>Your thumbnail will appear here</p>
            </div>
          </div>
        )}

        {isGenerating && (
          <div className="aspect-video rounded-2xl bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-orange-500/20 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
            <div className="text-center z-10">
              <Sparkles className="w-12 h-12 mx-auto mb-4 text-purple-500 animate-pulse" />
              <p className={`${textPrimary} font-medium`}>Creating your thumbnail...</p>
            </div>
          </div>
        )}

        {hasGenerated && !isGenerating && (
          <div className="space-y-4 animate-fadeIn">
            <div className="aspect-video rounded-2xl bg-gradient-to-br from-purple-600 via-pink-600 to-orange-600 flex items-center justify-center relative overflow-hidden shadow-2xl animate-scaleIn">
              <div className="text-center text-white z-10">
                <h3 className="text-4xl font-bold mb-2 animate-slideUp">AI Thumbnail</h3>
                <p
                  className="text-lg opacity-90 animate-slideUp"
                  style={{ animationDelay: "0.1s" }}
                >
                  Your Creative Vision
                </p>
              </div>
              <div className="absolute inset-0 bg-black/10"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shine"></div>
            </div>

            <div className="flex gap-3">
              <button
                className="flex-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95"
                onClick={() => alert("Downloading...")}
              >
                <Download className="w-4 h-4" /> Download
              </button>

              <button
                onClick={handleRegenerate}
                className={`flex-1 ${inputBg} border py-3 rounded-xl font-medium hover:border-purple-400 transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95`}
              >
                <RefreshCw className="w-4 h-4" /> Regenerate
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Recent Generations */}
      <div className="mt-8">
        <h3 className={`text-sm font-medium ${textSecondary} mb-4`}>Recent Generations</h3>
        <div className="grid grid-cols-3 gap-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className={`aspect-video rounded-lg bg-gradient-to-br ${
                isDarkMode ? "from-zinc-900 to-black border border-zinc-800" : "from-purple-200 to-pink-200"
              } hover:scale-105 transition-transform duration-300 cursor-pointer shadow-md hover:shadow-lg animate-fadeIn`}
              style={{ animationDelay: `${i * 0.1}s` }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
}
