import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "../pages/HomePage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import SplashPage from "../pages/SplashPage.jsx";
import SignUpPage from "../pages/SignUpPage.jsx";


export default function Router() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<SplashPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path ="/signup" element={<SignUpPage />} />
                <Route path="/home" element={<HomePage />} />
            </Routes>
        </BrowserRouter>
    );
}