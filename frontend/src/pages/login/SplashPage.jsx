import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import main from '../../assets/images/main.png';

// 스플래시 페이지 - 앱 시작 시 1.5초 후 로그인 페이지로 이동
export default function SplashPage() {
  const navigate = useNavigate();
  const [fade, setFade] = useState(true);

  useEffect(() => {
    // 1초 후 페이드 아웃 시작
    const timer1 = setTimeout(() => {
      setFade(false);
    }, 1000);

    // 1.5초 후 로그인 페이지로 이동
    const timer2 = setTimeout(() => {
      navigate('/login'); // 이동
    }, 1500);

    // 컴포넌트 언마운트 시 타이머 정리
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  return (
    <div
      className={`h-screen flex flex-col justify-between bg-primary pb-24 pt-40 text-white text-2xl font-semibold transition-opacity duration-500 ${
        fade ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {/*텍스트*/}
      <div className="px-8">
        <p className="mt-2">반갑습니다!</p>
        <p className="mt-2">Routick에 오신 것을</p>
        <p className="mt-2">환영합니다</p>
      </div>

      {/*이미지*/}
      <div className="flex justify-end">
        <img src={main} className="w-80 h-80 object-contain" />
      </div>
    </div>
  );
}
