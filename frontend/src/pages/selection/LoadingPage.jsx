import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/images/logo.png';

// 로딩 페이지
export default function LoadingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/map');
    }, 3000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-white gap-16">
      {/*로고*/}
      <img src={logo} alt="Routick" className="w-40 object-contain" />

      {/*프로그레스 바*/}
      <div className="flex flex-col items-center gap-3 w-full px-12">
        <div className="w-full h-1 bg-line1 rounded-full overflow-hidden">
          <div className="h-full bg-primary rounded-full animate-[loading_3s_ease-in-out_forwards]" />
        </div>
        <p className="text-14-rg text-gray2">
          딱 맞는 여행 코스를 찾고있어요✈️
        </p>
      </div>
    </div>
  );
}
