import React, { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { setAspectRatio, setPlatform, setProvider, setPrompt, startGenerating, finishGenerating } from "../../redux/homeSlice";
import { setImageUrl } from "../../redux/imagesUrlSlice";
import { Upload, Sparkles, RefreshCw, X } from "lucide-react";
import { generateThumbnail } from "../../api/apiService";

export default function DesignSettings() {
  const dispatch = useDispatch();
  const { aspectRatio, platform, provider, prompt, isGenerating, isDarkMode } = useSelector((state) => state.home);

  const aspectRatios = ["16:9", "9:16", "1:1", "4:5"];
  const platforms = ["YouTube", "Instagram", "Blog", "Podcast", "Twitter"];
  const providers = ["OpenAI", "Gemini", "Both"];

  const inputBg = isDarkMode ? "bg-black border-neutral-900 text-white" : "bg-white border-purple-200 text-gray-900";
  const textPrimary = isDarkMode ? "text-white" : "text-gray-900";
  const textSecondary = isDarkMode ? "text-neutral-500" : "text-gray-600";
  const cardBg = isDarkMode ? "bg-neutral-950 backdrop-blur-xl border-neutral-900" : "bg-white/80 backdrop-blur-xl border-purple-200/50";

  const fileInputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState("");
  const [image, setImage] = useState();
  // const [socket, setSocket] = useState(null);
  const [progress, setProgress] = useState(0);
  const wsRef = useRef(null);

  const handleGenerate = async () => {
    dispatch(startGenerating());

    const formData = new FormData();
    formData.append("aspect_ratio", aspectRatio);
    formData.append("platform", platform);
    formData.append("generator_provider", provider);
    formData.append("user_query", prompt);
    formData.append("reference_images", image);

    try {
      const data = await generateThumbnail(formData);

      const { job_id } = data;
      if (job_id) {
        connectWebSocket(job_id);
      }
    } catch (err) {
      console.error("Error preparing form data:", err);
    }
  };

  const connectWebSocket = (jobId) => {
    const wsUrl = import.meta.env.VITE_API_BASE_URL + `/${jobId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    // setSocket(ws);

    ws.onopen = () => {
      // console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        // console.log("WebSocket Message:", msg);

        const { progress, status, generated_images } = msg;
        if (progress !== undefined) setProgress(progress);

        if (generated_images && Array.isArray(generated_images) && generated_images.length > 0) {
          console.log(generated_images[0]);
          dispatch(setImageUrl(generated_images[0]));
        }

        if (progress === 100 && generated_images?.length > 0 && status === "completed") {
          // console.log("Thumbnail generation complete 🎉 Closing socket...");
          ws.close();
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = () => {
      dispatch(finishGenerating());
      // console.log("WebSocket disconnected");
    };

    ws.onerror = (error) => {
      dispatch(finishGenerating());
      console.error("WebSocket error:", error);
    };
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setImage(file);

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
      setFileName(file.fileName);
    } else {
      alert("Please select a valid image file (PNG, JPG, JPEG)");
    }
  };

  const removeImage = () => {
    setPreview(null);
    setFileName("");
    setImage(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className={`${cardBg} border rounded-3xl p-8 shadow-xl`}>
      <h2 className={`text-xl font-semibold ${textPrimary} mb-6 flex items-center gap-2`}>
        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse"></div>
        Design Settings
      </h2>

      {/* Aspect Ratio */}
      <div className="mb-6">
        <label className={`block text-sm font-medium ${textSecondary} mb-3`}>Aspect Ratio</label>
        <div className="grid grid-cols-4 gap-3">
          {aspectRatios.map((ratio) => (
            <button
              key={ratio}
              onClick={() => dispatch(setAspectRatio(ratio))}
              className={`py-3 px-4 rounded-xl font-medium ${
                aspectRatio === ratio ? "bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white" : `${inputBg} border hover:border-purple-400`
              } transition-all duration-300`}
            >
              {ratio}
            </button>
          ))}
        </div>
      </div>

      {/* Platform */}
      <div className="mb-6">
        <label className={`block text-sm font-medium ${textSecondary} mb-3`}>Platform</label>
        <div className="grid grid-cols-3 gap-3">
          {platforms.map((plat) => (
            <button
              key={plat}
              onClick={() => dispatch(setPlatform(plat))}
              className={`py-3 px-4 rounded-xl font-medium ${
                platform === plat ? "bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white" : `${inputBg} border hover:border-purple-400`
              } transition-all duration-300`}
            >
              {plat}
            </button>
          ))}
        </div>
      </div>

      {/* Provider */}
      <div className="mb-6">
        <label className={`block text-sm font-medium ${textSecondary} mb-3`}>AI Provider</label>
        <div className="grid grid-cols-3 gap-3">
          {providers.map((prov) => (
            <button
              key={prov}
              onClick={() => dispatch(setProvider(prov))}
              className={`py-3 px-4 rounded-xl font-medium ${
                provider === prov ? "bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white" : `${inputBg} border hover:border-purple-400`
              } transition-all duration-300`}
            >
              {prov}
            </button>
          ))}
        </div>
      </div>

      {/* Image Upload */}
      <div className="mb-6">
        <label className={`block text-sm font-medium ${textSecondary} mb-3`}>Background Image (Optional)</label>
        <div
          className="border-2 border-dashed rounded-xl p-8 text-center hover:border-purple-400 transition-all duration-300 cursor-pointer group"
          onClick={() => fileInputRef.current.click()}
        >
          {preview ? (
            <div className="relative inline-block w-full">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-48 object-cover rounded-xl border"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeImage();
                }}
                className="absolute top-2 right-2 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full p-1"
              >
                <X size={18} />
              </button>
              <p className="text-sm mt-2 text-gray-600">{fileName}</p>
            </div>
          ) : (
            <>
              <Upload className="w-8 h-8 mx-auto mb-3 text-gray-400 group-hover:text-purple-500 transition-colors" />
              <p className="text-sm text-gray-500 mb-1">Click to upload your image</p>
              <p className="text-xs text-gray-400 opacity-60">PNG, JPG up to 10MB</p>
            </>
          )}
        </div>

        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* Prompt */}
      <div className="mb-6">
        <label className={`block text-sm font-medium ${textSecondary} mb-3`}>Describe Your Vision</label>
        <textarea
          value={prompt}
          onChange={(e) => dispatch(setPrompt(e.target.value))}
          placeholder="e.g., Modern tech podcast thumbnail..."
          className={`w-full ${inputBg} border rounded-xl p-4 h-32 resize-none focus:ring-2 focus:ring-purple-500 transition-all duration-300`}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={isGenerating}
        className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50"
      >
        {isGenerating ? (
          <>
            <RefreshCw className="w-5 h-5 animate-spin" /> Generating...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" /> Generate Thumbnail
          </>
        )}
      </button>
    </div>
  );
}
