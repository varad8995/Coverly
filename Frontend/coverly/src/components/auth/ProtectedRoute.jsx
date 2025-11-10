import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../api/supabaseClient";
import { setUser, clearUser } from "../../redux/authSlice";
import { showLoader, hideLoader } from "../../redux/homeSlice";
import Loader from "../utilities/Loader";

export default function ProtectedRoute({ children }) {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [authLoaded, setAuthLoaded] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      dispatch(showLoader());
      const { data, error } = await supabase.auth.getSession();
      const session = data?.session;

      if (session) {
        dispatch(setUser({ user: session.user, session }));
        setIsAuthenticated(true);
      } else {
        dispatch(clearUser());
        setIsAuthenticated(false);
        navigate("/");
      }

      setAuthLoaded(true);
      dispatch(hideLoader());
    };

    initAuth();

    // Subscribe to auth changes (login/logout/refresh)
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        dispatch(setUser({ user: session.user, session }));
        setIsAuthenticated(true);
      } else {
        dispatch(clearUser());
        setIsAuthenticated(false);
        navigate("/");
      }
    });

    return () => {
      subscription.subscription.unsubscribe();
    };
  }, [dispatch, navigate]);

  if (!authLoaded) {
    return <Loader />;
  }
  return children;
}
