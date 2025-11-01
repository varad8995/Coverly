import axios from "axios";
import { supabase } from "../api/supabaseClient";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
});


api.interceptors.request.use(
    async (config) => {
        const { data } = await supabase.auth.getSession();
        const token = data?.session?.access_token;
        console.log("Interceptor Token:", token);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// api.interceptors.request.use(async (config) => {
//     // const token = localStorage.getItem("authToken");
//     const { data } = await supabase.auth.getSession();
//     const token = data?.session?.access_token;

//     if (token) {
//         config.headers.Authorization = `Bearer ${token}`;
//     }

//     return config;
// },
//     (error) => Promise.reject(error)
// );

export default api;