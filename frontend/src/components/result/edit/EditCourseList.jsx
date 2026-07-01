// import {
//   DndContext,
//   closestCenter,
//   PointerSensor,
//   useSensor,
//   useSensors,
// } from '@dnd-kit/core';
// import {
//   SortableContext,
//   verticalListSortingStrategy,
// } from '@dnd-kit/sortable';
// import EditCourseItem from './EditCourseItem.jsx';
// import DayHeader from './DayHeader.jsx';
//
// // 편집 모드 - 전체 코스 드래그 정렬 + 체크박스 삭제
// // DndContext를 최상위에 두어 day 간 장소 이동 가능
// export default function EditCourseList({
//   course,
//   selectedDay,
//   onDaySelect,
//   checkedPlaces,
//   onCheck,
//   onDragEnd,
// }) {
//   // 8px 이상 움직여야 드래그 시작 (체크박스 클릭과 구분)
//   const sensors = useSensors(
//     useSensor(PointerSensor, {
//       activationConstraint: { distance: 8 },
//     })
//   );
//
//   return (
//     <DndContext
//       sensors={sensors}
//       collisionDetection={closestCenter}
//       onDragEnd={onDragEnd}
//     >
//       <div className="flex flex-col gap-12">
//         {course.map((dayData, dayIndex) => (
//           <div key={dayData.day}>
//             {/*day 헤더*/}
//             <DayHeader
//               day={dayData.day}
//               showRefresh={false}
//               isSelected={selectedDay === dayData.day}
//               onClick={() => onDaySelect(dayData.day)}
//             />
//
//             {/*day별 장소 리스트 - uniqueId로 day 간 중복 방지*/}
//             <SortableContext
//               items={dayData.places.map((p) => `${dayData.day}-${p.id}`)}
//               strategy={verticalListSortingStrategy}
//             >
//               {dayData.places.map((place, index) => (
//                 <EditCourseItem
//                   key={`${dayData.day}-${place.id}`}
//                   place={{ ...place, uniqueId: `${dayData.day}-${place.id}` }}
//                   index={index}
//                   isChecked={checkedPlaces.some(
//                     (p) => p.dayIndex === dayIndex && p.placeIndex === index
//                   )}
//                   onCheck={() => onCheck(dayIndex, index)}
//                 />
//               ))}
//             </SortableContext>
//           </div>
//         ))}
//       </div>
//     </DndContext>
//   );
// }
