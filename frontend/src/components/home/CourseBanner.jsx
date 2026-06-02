import RightIcon from '../../assets/icons/right.svg?react';

// 배너
export default function CourseBanner({ name, image, onClick, className = '' }) {
  return (
    <div className={`flex gap-2 w-full ${className}`}>
      {/*텍스트*/}
      <div className="flex flex-col gap-6">
        <p className="text-primary text-10-sb">
          {name}님 취향을 분석해 여행을 추천해 드려요
        </p>
        <div className="text-black1 text-24-sb">
          <p className="none">취향에 맞는</p>
          <p>여행 코스</p>
          <div className="flex gap-3">
            <p>찾아볼까요?</p>
            <RightIcon className="w-5 h-10 -translate-y-1" onClick={onClick} />
          </div>
        </div>
      </div>

      {/*이미지*/}
      <img className="w-33 h-44 object-cover" src={image} alt="banner" />
    </div>
  );
}
