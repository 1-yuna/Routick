import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import MenuIcon from '../../../assets/icons/menu.svg?react';

// 편집 모드 - 코스 리스트 아이템
export default function EditCourseItem({ place, index, isChecked, onCheck }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: place.uniqueId });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-3 bg-white rounded-[10px] p-3 mb-2"
    >
      {/*체크박스*/}
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-primary border-primary' : 'border-line2'}`}
      >
        {isChecked && <span className="text-white text-10-sb">✓</span>}
      </button>

      {/*번호 + 이름/설명*/}
      <div className="flex items-center gap-2 flex-1">
        <span className="text-12-sb text-gray2">{index + 1}</span>
        <div className="flex flex-col">
          <p className="text-14-sb text-black1">{place.name}</p>
          <p className="text-12-rg text-gray2">{place.description}</p>
        </div>
      </div>

      {/*드래그 핸들*/}
      <div
        {...attributes}
        {...listeners}
        className="flex-shrink-0 cursor-grab"
        style={{ touchAction: 'none' }}
      >
        <MenuIcon className="w-5 h-5 text-gray2" />
      </div>
    </div>
  );
}
