import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "../pages/HomePage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import SplashPage from "../pages/SplashPage.jsx";
import SignupPage from "../pages/SignupPage.jsx";
import MyPage from "../pages/MyPage.jsx";
import CourseAddressPage from "../pages/CourseAddressPage.jsx";
import CoursePreferencePage from "../pages/CoursePreferencePage.jsx";
import CoursePreferenceDetailPage from "../pages/CoursePreferenceDetailPage.jsx";
import MapResultPage from "../pages/MapResultPage.jsx";


export default function Router() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<SplashPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path ="/signup" element={<SignupPage />} />
                <Route path="/home" element={<HomePage />} />
                <Route path="/mypage" element={<MyPage />} />
                <Route path="/course/address" element={<CourseAddressPage />} />
                <Route path="/course/preference" element={<CoursePreferencePage />} />
                <Route path="/course/preference/detail" element={<CoursePreferenceDetailPage />} />
                <Route path="/map" element={<MapResultPage />} />
            </Routes>
        </BrowserRouter>
    );
}