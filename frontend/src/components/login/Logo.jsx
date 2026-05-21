import logo from '../../assets/images/logo.png';

// 로고 이미지
export default function Logo({ className = '' }) {
  return <img src={logo} className={`object-contain ${className}`} />;
}
