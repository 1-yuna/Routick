import { useLocation, useNavigate } from 'react-router-dom';

// 하단바 개별 버튼 - 현재 경로와 일치하면 활성화 스타일 적용
export default function BottomBarButton({ icon: Icon, label, path }) {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = location.pathname === path;

  return (
    <button
      className="flex flex-col items-center text-10-rg"
      onClick={() => navigate(path)}
    >
      <Icon className="w-6 h-6" />

      {/*활성화 시 primary 색상 및 볼드체 적용*/}
      <p className={`${isActive ? 'text-primary text-10-sb' : 'text-black1'}`}>
        {label}
      </p>
    </button>
  );
}
