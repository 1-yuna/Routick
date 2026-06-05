import FullWidthInput from '../input/FullWidthInput.jsx';

// 회원가입 - 이메일 버튼
export default function InputWithButton({
  placeholder,
  type,
  buttonText,
  onButtonClick,
  className = '',
  buttonType = 'button',
}) {
  return (
    <div className="flex items-stretch">
      {/*이메일 입력 폼*/}
      <div className="flex-1">
        <FullWidthInput placeholder={placeholder} type={type} />
      </div>

      {/*버튼*/}
      <button
        type={buttonType}
        onClick={onButtonClick}
        className={`w-16 bg-primary text-white text-16-sb ${className}`}
      >
        {buttonText}
      </button>
    </div>
  );
}
