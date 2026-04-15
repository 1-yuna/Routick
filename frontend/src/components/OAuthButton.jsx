export default function OAuthButton({ icon, onClick, alt = "social login" }) {
    return (
        <button
            onClick={onClick}
            className="w-9 h-9 flex items-center justify-center"
        >
            <img
                src={icon}
                alt={alt}
                className="w-9 h-9 rounded-full object-cover"
            />
        </button>
    );
}