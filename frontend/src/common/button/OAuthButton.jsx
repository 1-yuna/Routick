export default function OAuthButton({ icon, onClick, alt = 'social login' }) {
  return (
    <button
      onClick={onClick}
      className="w-10 h-10 flex items-center justify-center"
    >
      <img
        src={icon}
        alt={alt}
        className="w-10 h-10 rounded-full object-cover"
      />
    </button>
  );
}
