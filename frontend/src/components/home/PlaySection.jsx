// 놀거리
import PlayCard from '../../common/card/PlayCard.jsx';

export default function PlaySection({
  className = '',
  onHotplace,
  onExhibition,
  onNature,
}) {
  return (
    <div className={`flex flex-col gap-6 bg-button ${className}`}>
      {/*텍스트*/}
      <p className="text-black1 text-16-sb">지금 즐기기 좋은 놀거리</p>
      <div className="flex gap-8">
        <PlayCard icon={'🔥'} text={'핫플'} onClick={onHotplace} />
        <PlayCard icon={'🎨'} text={'전시/문화'} onClick={onExhibition} />
        <PlayCard icon={'🌿'} text={'자연'} onClick={onNature} />
      </div>
    </div>
  );
}
