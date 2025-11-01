import React, { useState, useEffect } from "react";
import { Sparkles, Mail, Lock, User, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import "../../styles/coverlyAuth.css";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../api/supabaseClient.js";
import { setLoading, setUser, clearUser, setError } from "../../redux/authSlice.js";

export default function CoverlyAuth() {
  const dispatch = useDispatch();
  const { isDarkMode } = useSelector((state) => ({
    isDarkMode: state.home.isDarkMode,
  }));
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  let navigate = useNavigate();

  const bgClass = isDarkMode ? "bg-black" : "bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50";
  const cardBg = isDarkMode ? "bg-neutral-950 backdrop-blur-xl border-neutral-900" : "bg-white/80 backdrop-blur-xl border-purple-200/50";
  const textPrimary = isDarkMode ? "text-white" : "text-gray-900";
  const textSecondary = isDarkMode ? "text-neutral-500" : "text-gray-600";
  const inputBg = isDarkMode ? "bg-black border-neutral-900 text-white" : "bg-white border-purple-200 text-gray-900";

  useEffect(() => {
    const getSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session) {
        const jwtToken = session.access_token;
        console.log("JWT Token:", jwtToken);
        dispatch(setUser({ user: session.user, session }));
        navigate("/home");
      }
    };

    getSession();

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        dispatch(setUser({ user: session.user, session }));
        navigate("/home");
      } else {
        dispatch(clearUser());
      }
    });

    return () => subscription.subscription.unsubscribe();
  }, [dispatch, navigate]);

  const handleGoogleLogin = async () => {
    dispatch(setLoading(true));

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });

    if (error) {
      dispatch(setError(error.message));
      console.error("Login error:", error.message);
    }

    dispatch(setLoading(false));
  };

  const handleSubmit = () => {
    console.log("Form submitted:", formData);
    // navigate("/home");
  };

  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-500 flex items-center justify-center p-6`}>
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-20 left-10 w-72 h-72 ${isDarkMode ? "bg-purple-900/10" : "bg-purple-300/20"} rounded-full blur-3xl animate-float`}></div>
        <div
          className={`absolute bottom-20 right-10 w-96 h-96 ${isDarkMode ? "bg-pink-900/10" : "bg-pink-300/20"} rounded-full blur-3xl animate-float`}
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      {/* Auth Card */}
      <div className={`relative w-full max-w-md ${cardBg} border rounded-3xl shadow-2xl p-8 md:p-10 z-10 animate-scaleIn`}>
        {/* Logo */}
        <div className="flex items-center justify-center mb-8 animate-slideUp">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center shadow-lg animate-float">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
        </div>

        {/* Header */}
        <div
          className="text-center mb-8 animate-slideUp"
          style={{ animationDelay: "0.1s" }}
        >
          <h1 className={`text-3xl font-bold ${textPrimary} mb-2`}>{isLogin ? "Welcome Back" : "Create Account"}</h1>
          <p className={`${textSecondary}`}>{isLogin ? "Sign in to create stunning thumbnails" : "Join us to start creating amazing thumbnails"}</p>
        </div>

        {/* Form */}
        <div
          className="space-y-5 animate-slideUp"
          style={{ animationDelay: "0.2s" }}
        >
          {/* Name Field (Signup Only) */}
          {!isLogin && (
            <div className="animate-slideDown">
              <label className={`block text-sm font-medium ${textSecondary} mb-2`}>Full Name</label>
              <div className="relative">
                <User className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${textSecondary}`} />
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Enter your name"
                  className={`w-full ${inputBg} border rounded-xl pl-12 pr-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300`}
                />
              </div>
            </div>
          )}

          {/* Email Field */}
          <div>
            <label className={`block text-sm font-medium ${textSecondary} mb-2`}>Email</label>
            <div className="relative">
              <Mail className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${textSecondary}`} />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="Enter your email"
                className={`w-full ${inputBg} border rounded-xl pl-12 pr-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300`}
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label className={`block text-sm font-medium ${textSecondary} mb-2`}>Password</label>
            <div className="relative">
              <Lock className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${textSecondary}`} />
              <input
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter your password"
                className={`w-full ${inputBg} border rounded-xl pl-12 pr-12 py-3.5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className={`absolute right-4 top-1/2 -translate-y-1/2 ${textSecondary} hover:text-purple-500 transition-colors`}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Forgot Password (Login Only) */}
          {isLogin && (
            <div className="flex justify-end">
              <button
                type="button"
                className="text-sm text-purple-500 hover:text-purple-600 transition-colors"
              >
                Forgot password?
              </button>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white py-4 rounded-xl font-semibold text-lg shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 flex items-center justify-center gap-3 group transform hover:scale-105 active:scale-95"
          >
            {isLogin ? "Sign In" : "Create Account"}
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        {/* Divider */}
        <div
          className="relative my-8 animate-fadeIn"
          style={{ animationDelay: "0.3s" }}
        >
          <div className={`absolute inset-0 flex items-center`}>
            <div className={`w-full border-t ${isDarkMode ? "border-neutral-900" : "border-gray-200"}`}></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className={`px-4 ${isDarkMode ? "bg-neutral-950" : "bg-white"} ${textSecondary}`}>Or continue with</span>
          </div>
        </div>

        {/* Social Login */}
        <div
          className="grid grid-cols-1 gap-4 mb-8 animate-fadeIn"
          style={{ animationDelay: "0.4s" }}
        >
          <button
            className={`${inputBg} border py-3 rounded-xl font-medium hover:border-purple-400 transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95`}
            onClick={handleGoogleLogin}
          >
            <svg
              className="w-5 h-5"
              viewBox="0 0 24 24"
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            Google
          </button>
        </div>

        <div
          className={`text-center ${textSecondary} animate-fadeIn`}
          style={{ animationDelay: "0.5s" }}
        >
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="text-purple-500 hover:text-purple-600 font-medium transition-colors"
          >
            {isLogin ? "Sign Up" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}
