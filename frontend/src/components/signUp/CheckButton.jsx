export default function CheckButton({
  text,
  onClick,
  className = "",
  type = "button",
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`w-24 h-16 bg-primary text-white text-base font-normal ${className}`}
    >
      {text}
    </button>
  );
}