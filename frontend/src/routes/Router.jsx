import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SplashPage from '../pages/login/SplashPage.jsx';
import LoginPage from '../pages/login/LoginPage.jsx';
import SignupPage from '../pages/login/SignupPage.jsx';
import HomePage from '../pages/home/HomePage.jsx';
import AddressPage from '../pages/selection/AddressPage.jsx';
import AddressSearchPage from '../pages/selection/AddressSearchPage.jsx';
import CoursePreferencePage from '../pages/CoursePreferencePage.jsx';
import CoursePreferenceDetailPage from '../pages/CoursePreferenceDetailPage.jsx';
import MapResultPage from '../pages/MapResultPage.jsx';

import MyPage from '../pages/MyPage.jsx';
import MyTripPage from '../pages/MyTripPage.jsx';

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SplashPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/mytrip" element={<MyTripPage />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/course/address" element={<AddressPage />} />
        <Route path="/course/address/search" element={<AddressSearchPage />} />
        <Route path="/course/preference" element={<CoursePreferencePage />} />
        <Route
          path="/course/preference/detail"
          element={<CoursePreferenceDetailPage />}
        />
        <Route path="/map" element={<MapResultPage />} />
      </Routes>
    </BrowserRouter>
  );
}
