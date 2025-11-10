import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    user: null,
    session: null,
    error: null
};

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setUser: (state, action) => {
            state.user = action.payload.user;
            state.session = action.payload.session;
            state.error = null;
        },
        clearUser: (state) => {
            state.user = null;
            state.session = null;
        },
        setError: (state, action) => {
            state.error = action.payload;
            state.loading = false;
        },
    },
});

export const { setUser, clearUser, setError } = authSlice.actions;
export default authSlice.reducer;