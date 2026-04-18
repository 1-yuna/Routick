export default function RadioItem({ name, value, label, checked, onChange }) {
    return (
        <label className="flex items-center gap-2">
            <input
                className="w-5 h-5"
                type="radio"
                name={name}
                value={value}
                checked={checked}
                onClick={onChange}
                readOnly
            />
            {label}
        </label>
    );
}