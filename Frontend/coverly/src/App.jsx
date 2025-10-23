import { Route, Routes } from "react-router-dom";
import CoverlyAuth from "./components/auth/CoverlyAuth";
import Home from "./components/Home/Home";

function App() {
  return (
    <>
      <Routes>
        <Route
          path="/"
          element={<CoverlyAuth />}
        />
        <Route
          path="/home"
          element={
            // <ProtectedRoute user={null}>
            <Home />
            // </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
