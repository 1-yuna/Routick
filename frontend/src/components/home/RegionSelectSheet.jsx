import { useState } from 'react';
import CancelIcon from '../../assets/icons/cancel.svg?react';

// 지역 설정 바텀시트 - 좌측 카테고리(시/도) + 우측 세부 지역 2분할
export default function RegionSelectSheet({
  regions,
  selected,
  onSelect,
  onClose,
}) {
  const [activeCategory, setActiveCategory] = useState(selected.category);

  const activeRegion = regions.find((r) => r.category === activeCategory);

  const handleSelectArea = (area) => {
    onSelect({ category: activeCategory, area });
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end bg-black/40"
      onClick={onClose}
    >
      <div
        className="w-full h-[80vh] bg-white rounded-t-20 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/*헤더*/}
        <div className="flex items-center justify-between px-6 h-16 border-b border-line1 flex-shrink-0">
          <p className="text-16-sb text-black1">지역 설정</p>
          <button onClick={onClose}>
            <CancelIcon className="w-5 h-5 text-gray2" />
          </button>
        </div>

        {/*좌측 카테고리 + 우측 세부 지역*/}
        <div className="flex flex-1 overflow-hidden">
          {/*좌측 카테고리*/}
          <div className="w-32 flex-shrink-0 overflow-y-auto no-scrollbar bg-neutral">
            {regions.map((region) => {
              const isActive = region.category === activeCategory;
              return (
                <button
                  key={region.category}
                  onClick={() => setActiveCategory(region.category)}
                  className={`flex items-center justify-center w-32 h-14 text-14-sb ${
                    isActive ? 'bg-white text-primary' : 'bg-neutral text-gray2'
                  }`}
                >
                  {region.category}
                </button>
              );
            })}
          </div>

          {/*우측 세부 지역*/}
          <div className="flex-1 px-6 overflow-y-auto no-scrollbar">
            {activeRegion?.areas.map((area) => {
              const isSelected =
                selected.category === activeCategory && selected.area === area;
              return (
                <button
                  key={area}
                  onClick={() => handleSelectArea(area)}
                  className={`w-full h-14 flex items-center text-left border-b border-line1 text-14-sb ${
                    isSelected ? 'text-primary' : 'text-black1'
                  }`}
                >
                  {area}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
