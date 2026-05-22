// 선택 버튼
export default function SelectionGrid({ items, selected, onSelect }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {items.map((item) => (
        <button
          key={item.value}
          onClick={() => onSelect(selected === item.value ? '' : item.value)}
          className={`h-16 rounded-[10px] text-14-sb transition-colors
            ${
              selected === item.value
                ? 'bg-primaryOpacity text-primary'
                : 'bg-button text-gray2'
            }`}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
