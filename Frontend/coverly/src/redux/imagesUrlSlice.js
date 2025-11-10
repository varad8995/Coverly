import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    newImage: "",
    recentImages: []
}

const imagesUrlSlice = createSlice({
    name: "imagesurl",
    initialState,
    reducers: {
        setImageUrl: (state, action) => {
            if (action.payload) {
                state.newImage = action.payload;
                // state.recentImages = [...state.recentImages, state.newImage];
                state.recentImages.unshift(action.payload);
                if (state.recentImages.length > 3) {
                    state.recentImages = state.recentImages.slice(0, 3);
                }
                localStorage.setItem("recentImages", JSON.stringify(state.recentImages));
            }
        },
        setRecentImages: (state, action) => {
            state.recentImages = action.payload.slice(0, 3);
        },
        resetImageUrl: (state) => {
            state.newImage = "";
        },
    },
});

export const {
    setImageUrl,
    setRecentImages,
    resetImageUrl
} = imagesUrlSlice.actions;

export default imagesUrlSlice.reducer;