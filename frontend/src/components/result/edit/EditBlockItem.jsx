import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import MenuIcon from '../../../assets/icons/menu.svg?react';
import CheckIcon from '../../../assets/icons/check.svg?react';

// 편집 모드 - 블록 리스트 아이템 (place/parking 모두 표시)
// 체크박스 + 카드(번호/이름/설명) + 드래그 핸들
export default function EditBlockItem({ block, index, isChecked, onCheck }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: block.blockOrder });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const isParking = block.type === 'parking';

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-2 p-2 ${isChecked ? 'bg-button' : 'bg-white'}`}
    >
      {/* 체크박스 */}
      <button
        onClick={onCheck}
        className={`w-6 h-6 rounded-full border flex items-center justify-center flex-shrink-0 ${
          isChecked ? 'bg-primary border-primary' : 'border-line2'
        }`}
      >
        {isChecked && <CheckIcon className="w-3 h-3 text-white" />}
      </button>

      {/* 카드 */}
      <div className="flex items-center gap-3 px-2 py-3 flex-1 bg-white rounded-5 shadow-md">
        {/* 번호/P dot */}
        <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 bg-line2">
          <span className="text-12-sb text-white">
            {isParking ? 'P' : index}
          </span>
        </div>

        {/* 이름/설명 */}
        <div className="flex flex-col gap-1 flex-1">
          <p className="text-14-sb text-black1">{block.name}</p>
          {isParking ? (
            block.fee && <p className="text-10-rg text-gray2">{block.fee}</p>
          ) : (
            <p className="text-10-rg text-gray2 line-clamp-2">
              {block.description}
            </p>
          )}
        </div>
      </div>

      {/* 드래그 핸들 */}
      <div
        {...attributes}
        {...listeners}
        className="flex-shrink-0 cursor-grab"
        style={{ touchAction: 'none' }}
      >
        <MenuIcon className="w-[30px] h-[30px] text-gray2" />
      </div>
    </div>
  );
}
