import { configureStore } from "@reduxjs/toolkit";
import homeReducer from "./homeSlice";
import authReducer from "./authSlice";
import imagesUrlReducer from "./imagesUrlSlice";

export const store = configureStore({
    reducer: {
        home: homeReducer,
        auth: authReducer,
        imagesurl: imagesUrlReducer,
    },
});