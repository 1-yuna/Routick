// 공통 선택 버튼 그리드
// - selected가 배열이면 다중 선택, 문자열이면 단일 선택
// - 선택된 항목은 primaryOpacity 배경, 미선택은 button 배경
export default function SelectionGrid({ items, selected, onSelect }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {items.map((item) => {
        const isSelected = Array.isArray(selected)
          ? selected.includes(item.value)
          : selected === item.value;

        return (
          <button
            key={item.value}
            onClick={() => {
              if (Array.isArray(selected)) {
                onSelect(item.value);
              } else {
                onSelect(selected === item.value ? '' : item.value);
              }
            }}
            className={`h-16 rounded-[10px] text-14-sb transition-colors
              ${
                isSelected
                  ? 'bg-primaryOpacity text-primary'
                  : 'bg-button text-gray2'
              }`}
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}
