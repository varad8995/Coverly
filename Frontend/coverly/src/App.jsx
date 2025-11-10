import { Route, Routes } from "react-router-dom";
import CoverlyAuth from "./components/auth/CoverlyAuth";
import Home from "./components/Home/Home";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import Loader from "./components/utilities/Loader";

function App() {
  return (
    <>
      <ProtectedRoute>
        <Loader />
        <Routes>
          <Route
            path="/"
            element={<CoverlyAuth />}
          />
          <Route
            path="/home"
            element={<Home />}
          />
        </Routes>
      </ProtectedRoute>
    </>
  );
}

export default App;
