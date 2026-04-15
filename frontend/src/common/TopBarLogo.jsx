import logo from '../assets/logo.png';

// TopBar + 로고
export default function TopBarLogo({ onClick }) {
    return (
        <button onClick={onClick} className="fixed top-0 left-0 w-full h-28 flex bg-white items-end px-4">
            <img className="w-32 h-16 object-contain" src={logo} />
        </button>
    );
}