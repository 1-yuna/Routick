import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import SplashPage from '../pages/login/SplashPage.jsx';
import LoginPage from '../pages/login/LoginPage.jsx';
import SignupPage from '../pages/login/SignupPage.jsx';
import OAuthRedirectPage from '../pages/login/OAuthRedirectPage.jsx';
import HomePage from '../pages/home/HomePage.jsx';
import PlayListPage from '../pages/home/PlayListPage.jsx';
import PlaceDetailPage from '../pages/place/PlaceDetailPage.jsx';
import TravelPeriodPage from '../pages/selection/TravelPeriodPage.jsx';
import DatePage from '../pages/selection/DatePage.jsx';
import TransportPage from '../pages/selection/TransportPage.jsx';
import RoutePage from '../pages/selection/RoutePage.jsx';
import AddressPage from '../pages/selection/AddressPage.jsx';
import AddressSearchPage from '../pages/selection/AddressSearchPage.jsx';
import CompanionPage from '../pages/selection/CompanionPage.jsx';
import MoodPage from '../pages/selection/MoodPage.jsx';
import ActivityPage from '../pages/selection/ActivityPage.jsx';
import DislikeActivityPage from '../pages/selection/DislikeActivityPage.jsx';
import LoadingPage from '../pages/selection/LoadingPage.jsx';
import FailPage from '../pages/selection/FailPage.jsx';
import ResultPage from '../pages/result/ResultPage.jsx';
import PlaceEditPage from '../pages/result/PlaceEditPage.jsx';
import MyTripPage from '../pages/myTrip/MyTripPage.jsx';
import MyTripEditPage from '../pages/myTrip/MyTripEditPage.jsx';
import MyPage from '../pages/myProfile/MyPage.jsx';
import MyEditPage from '../pages/myProfile/MyEditPage.jsx';
import useUserStore from '../store/userStore.jsx';
import { getMe } from '../api/user.jsx';

const PUBLIC_PATHS = ['/', '/login', '/signup', '/oauth/redirect'];

// 새로고침 등으로 Splash를 거치지 않고 바로 들어온 경우 user 채우기
function AuthBoot({ children }) {
  const location = useLocation();
  const user = useUserStore((state) => state.user);
  const setUser = useUserStore((state) => state.setUser);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (user || PUBLIC_PATHS.includes(location.pathname)) {
      setChecked(true);
      return;
    }
    (async () => {
      try {
        const res = await getMe();
        setUser(res.data.data);
      } catch (e) {
        // 실패해도 각 페이지 API 호출이 401로 자연스럽게 처리됨
      } finally {
        setChecked(true);
      }
    })();
  }, []);

  if (!checked) return null;
  return children;
}

export default function Router() {
  return (
    <BrowserRouter>
      <AuthBoot>
        <Routes>
          <Route path="/" element={<SplashPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/oauth/redirect" element={<OAuthRedirectPage />} />

          <Route path="/home" element={<HomePage />} />
          <Route path="/playlist" element={<PlayListPage />} />
          <Route path="/place/:id" element={<PlaceDetailPage />} />
          <Route path="/place/edit/:id" element={<PlaceEditPage />} />

          <Route path="/select/period" element={<TravelPeriodPage />} />
          <Route path="/select/date" element={<DatePage />} />
          <Route path="/select/transport" element={<TransportPage />} />
          <Route path="/select/route" element={<RoutePage />} />
          <Route path="/select/address" element={<AddressPage />} />
          <Route
            path="/select/address/search"
            element={<AddressSearchPage />}
          />
          <Route path="/select/companion" element={<CompanionPage />} />
          <Route path="/select/mood" element={<MoodPage />} />
          <Route path="/select/activity" element={<ActivityPage />} />
          <Route path="/select/dislike" element={<DislikeActivityPage />} />
          <Route path="/loading" element={<LoadingPage />} />
          <Route path="/fail" element={<FailPage />} />

          <Route path="/result" element={<ResultPage />} />

          <Route path="/mytrip" element={<MyTripPage />} />
          <Route path="/mytrip/edit/:id" element={<MyTripEditPage />} />

          <Route path="/mypage" element={<MyPage />} />
          <Route path="/my/profile" element={<MyEditPage />} />
        </Routes>
      </AuthBoot>
    </BrowserRouter>
  );
}
