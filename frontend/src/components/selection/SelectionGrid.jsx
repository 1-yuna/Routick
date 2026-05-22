// 선택 버튼
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
            onClick={() => onSelect(item.value)}
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
