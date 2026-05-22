// 하단바 버튼
import { useLocation, useNavigate } from 'react-router-dom';

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
      <p className={`${isActive ? 'text-primary text-10-sb' : 'text-black1'}`}>
        {label}
      </p>
    </button>
  );
}
