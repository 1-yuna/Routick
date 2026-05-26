import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SplashPage from '../pages/login/SplashPage.jsx';
import LoginPage from '../pages/login/LoginPage.jsx';
import SignupPage from '../pages/login/SignupPage.jsx';
import HomePage from '../pages/home/HomePage.jsx';
import PlayListPage from '../pages/home/PlayListPage.jsx';
import PlaceDetailPage from '../pages/place/PlaceDetailPage.jsx';
import AddressPage from '../pages/selection/AddressPage.jsx';
import AddressSearchPage from '../pages/selection/AddressSearchPage.jsx';
import TravelPeriodPage from '../pages/selection/TravelPeriodPage.jsx';
import CompanionPage from '../pages/selection/CompanionPage.jsx';
import AgeGroupPage from '../pages/selection/AgeGroupPage.jsx';
import MoodPage from '../pages/selection/MoodPage.jsx';
import ActivityPage from '../pages/selection/ActivityPage.jsx';
import TransportPage from '../pages/selection/TransportPage.jsx';
import DislikeActivityPage from '../pages/selection/DislikeActivityPage.jsx';
import LoadingPage from '../pages/selection/LoadingPage.jsx';
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
        <Route path="/playlist" element={<PlayListPage />} />
        <Route path="/place/:id" element={<PlaceDetailPage />} />

        <Route path="/select/address" element={<AddressPage />} />
        <Route path="/select/address/search" element={<AddressSearchPage />} />
        <Route path="/select/period" element={<TravelPeriodPage />} />
        <Route path="/select/companion" element={<CompanionPage />} />
        <Route path="/select/age" element={<AgeGroupPage />} />
        <Route path="/select/mood" element={<MoodPage />} />
        <Route path="/select/activity" element={<ActivityPage />} />
        <Route path="/select/transport" element={<TransportPage />} />
        <Route path="/select/dislike" element={<DislikeActivityPage />} />
        <Route path="/loading" element={<LoadingPage />} />

        <Route path="/map" element={<MapResultPage />} />

        <Route path="/mytrip" element={<MyTripPage />} />
        <Route path="/mypage" element={<MyPage />} />
      </Routes>
    </BrowserRouter>
  );
}
