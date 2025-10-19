import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    aspectRatio: "16:9",
    platform: "YouTube",
    prompt: "",
    isGenerating: false,
    hasGenerated: false,
    isDarkMode: false
}

const homeSlice = createSlice({
    name: "home",
    initialState,
    reducers: {
        setAspectRatio: (state, action) => {
            state.aspectRatio = action.payload;
        },
        setPlatform: (state, action) => {
            state.platform = action.payload;
        },
        setPrompt: (state, action) => {
            state.prompt = action.payload;
        },
        toggleDarkMode: (state) => {
            state.isDarkMode = !state.isDarkMode;
        },
        startGenerating: (state) => {
            state.isGenerating = true;
        },
        finishGenerating: (state) => {
            state.isGenerating = false;
            state.hasGenerated = true;
        },
        resetGeneration: (state) => {
            state.hasGenerated = false;
        },
    },
});

export const {
    setAspectRatio,
    setPlatform,
    setPrompt,
    toggleDarkMode,
    startGenerating,
    finishGenerating,
    resetGeneration,
} = homeSlice.actions;

export default homeSlice.reducer;