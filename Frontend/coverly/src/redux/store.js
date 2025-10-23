import { configureStore } from "@reduxjs/toolkit";
import homeReducer from "./homeSlice";
import authReducer from "./authSlice";

export const store = configureStore({
    reducer: {
        home: homeReducer,
        auth: authReducer
    },
});