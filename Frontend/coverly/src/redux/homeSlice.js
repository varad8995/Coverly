import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    aspectRatio: "16:9",
    platform: "YouTube",
    provider: "Gemini",
    prompt: "",
    isGenerating: false,
    hasGenerated: false,
    isDarkMode: true,
    loading: false,
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
        setProvider: (state, action) => {
            state.provider = action.payload;
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
        showLoader: (state) => {
            state.loading = true;
        },
        hideLoader: (state) => {
            state.loading = false;
        }
    },
});

export const {
    setAspectRatio,
    setPlatform,
    setProvider,
    setPrompt,
    toggleDarkMode,
    startGenerating,
    finishGenerating,
    resetGeneration,
    showLoader,
    hideLoader
} = homeSlice.actions;

export default homeSlice.reducer;