import TagButton from "./TagButton";

export default function TagSelectGroup({
                                           question,
                                           description,
                                           options,
                                           value,
                                           onChange
                                       }) {
    const handleClick = (selectedValue) => {
        if (value.includes(selectedValue)) {
            // 선택 해제
            onChange(value.filter((v) => v !== selectedValue));
        } else {
            // 선택 추가
            onChange([...value, selectedValue]);
        }
    };

    return (
        <div className="flex flex-col pb-8">
            <div>
                <p className="font-bold text-base">{question}</p>
                {description && (
                    <p className="font-bold text-base pb-4">{description}</p>
                )}
            </div>

            <div className="flex flex-wrap gap-x-5 gap-y-2">
                {options.map((item) => (
                    <TagButton
                        key={item.value}
                        label={item.label}
                        selected={value.includes(item.value)}
                        onClick={() => handleClick(item.value)}
                    />
                ))}
            </div>
        </div>
    );
}