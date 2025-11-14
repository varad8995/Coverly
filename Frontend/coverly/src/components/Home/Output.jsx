import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Sparkles, Download, RefreshCw, Image, Loader2 } from "lucide-react";
import { resetGeneration } from "../../redux/homeSlice";
import { resetImageUrl } from "../../redux/imagesUrlSlice";
import "../../styles/animations.css";

export default function Output() {
  const dispatch = useDispatch();
  const { isGenerating, hasGenerated, isDarkMode, progress, socketMessage } = useSelector((state) => state.home);
  const imageUrl = useSelector((state) => state.imagesurl.newImage);
  const recentImages = useSelector((state) => state.imagesurl.recentImages);

  const cardBg = isDarkMode ? "bg-neutral-950 backdrop-blur-xl border-neutral-900" : "bg-white/80 backdrop-blur-xl border-purple-200/50";
  const textPrimary = isDarkMode ? "text-white" : "text-gray-900";
  const textSecondary = isDarkMode ? "text-neutral-500" : "text-gray-600";
  const inputBg = isDarkMode ? "bg-black border-neutral-900 text-white" : "bg-white border-purple-200 text-gray-900";

  useEffect(() => {
    const storedRecentImages = localStorage.getItem("recentImages");
    if (storedRecentImages) {
      const parsedImages = JSON.parse(storedRecentImages);
      if (Array.isArray(parsedImages)) {
        dispatch({ type: "imagesurl/setRecentImages", payload: parsedImages });
      }
    }
  }, [dispatch]);

  const handleRegenerate = () => {
    dispatch(resetGeneration());
    dispatch(resetImageUrl());
  };

  const handleDownload = async (presignedUrl) => {
    try {
      const response = await fetch("https://coverly-hogj.onrender.com/api/download-photo/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ presigned_url: presignedUrl })
      });

      if (!response.ok) {
        throw new Error("Failed to download file");
      }

      // Convert StreamingResponse to Blob
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      // Trigger browser download
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `thumbnail_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error("Download error:", error);
    }
  };

  const handleGeneratedImageDownload = () => {
    if (!imageUrl) {
      alert("No image available to download!");
      return;
    }
    handleDownload(imageUrl);
  };

  return (
    <div className={`${cardBg} border rounded-3xl p-8 shadow-xl transition-all duration-500 animate-slideInRight right-output-section`}>
      <div className="mb-6">
        <h2 className={`text-xl font-semibold ${textPrimary} mb-6 flex items-center gap-2`}>
          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse"></div>
          Your Thumbnail
        </h2>

        {isGenerating && (
          <div className="space-y-3 animate-fadeIn">
            {/* Progress bar */}
            <div className={`relative h-3 ${isDarkMode ? "bg-neutral-900" : "bg-gray-200"} rounded-full overflow-hidden`}>
              <div
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 transition-all duration-500 ease-out rounded-full"
                style={{ width: `${Math.min(progress, 100)}%` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
              </div>
            </div>

            {/* Progress info */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-purple-500 animate-spin" />
                <span className={`text-sm font-medium ${textPrimary}`}>{socketMessage}</span>
              </div>
              <span className={`text-sm font-bold ${textPrimary}`}>{Math.round(progress)}%</span>
            </div>
          </div>
        )}
      </div>

      {/* Output area */}
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
              <img
                src={imageUrl}
                alt="Generated Thumbnail"
                className="w-full h-full object-cover rounded-2xl relative z-10"
              />
              <div className="absolute inset-0 bg-black/10"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shine"></div>
            </div>

            <div className="flex gap-3">
              <button
                className="flex-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95 cursor-pointer"
                onClick={handleGeneratedImageDownload}
              >
                <Download className="w-4 h-4" /> Download
              </button>

              <button
                onClick={handleRegenerate}
                className={`flex-1 ${inputBg} border py-3 rounded-xl font-medium hover:border-purple-400 transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95 cursor-pointer`}
              >
                <RefreshCw className="w-4 h-4" /> Regenerate
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Recent Generated Images */}
      <div className="mt-8">
        <h3 className={`text-sm font-medium ${textSecondary} mb-4`}>Recent Generations</h3>
        <div className="grid grid-cols-3 gap-3">
          {recentImages.map((url, index) => (
            <div
              key={index}
              onClick={() => handleDownload(url)}
              className="hover:scale-105 transition-transform duration-300 cursor-pointer shadow-md hover:shadow-lg animate-fadeIn"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <img
                src={url}
                alt={`Generated ${index + 1}`}
                loading="lazy"
                className="w-full h-full object-cover rounded-lg transition-transform duration-300 group-hover:scale-105"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
