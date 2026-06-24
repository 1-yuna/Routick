import PlayCard from '../../common/card/PlayCard.jsx';

// 홈 - 놀거리 섹션 (핫플/문화·자연/맛집·카페)
export default function PlaySection({
  className = '',
  onHotplace,
  onCultureNature,
  onFoodCafe,
}) {
  return (
    <div className={`flex flex-col gap-6 bg-button ${className}`}>
      {/*텍스트*/}
      <p className="text-black1 text-16-sb">지금 즐기기 좋은 놀거리</p>

      {/*카드*/}
      <div className="flex gap-8">
        <PlayCard icon={'🔥'} text={'핫플'} onClick={onHotplace} />
        <PlayCard icon={'🍽️'} text={'맛집/카페'} onClick={onFoodCafe} />
        <PlayCard icon={'🎨'} text={'문화/자연'} onClick={onCultureNature} />
      </div>
    </div>
  );
}
