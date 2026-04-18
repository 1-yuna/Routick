// RadioGroup.jsx
import RadioItem from "./RadioItem.jsx";

export default function RadioGroup({
                                       question,
                                       name,
                                       value,
                                       options,
                                       onChange
                                   }) {
    const handleChange = (e) => {
        const selectedValue = e.target.value;

        if (value === selectedValue) {
            onChange({ target: { value: "" } }); // 같은 거 누르면 해제
        } else {
            onChange(e);
        }
    };


    return (
        <div className="flex flex-col pb-8">
            <p className="font-bold text-base pb-2">{question}</p>

            <div className="flex flex-wrap gap-x-5 gap-y-2">
                {options.map((item) => (
                    <RadioItem
                        key={item.value}
                        name={name}
                        value={item.value}
                        label={item.label}
                        checked={value === item.value}
                        onChange={handleChange}
                    />
                ))}
            </div>
        </div>
    );
}