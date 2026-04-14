import Router from "./routes/Router";

export default function App() {
    return (
        <div className="min-h-screen bg-gray-100 flex justify-center">
            <div className="w-full max-w-6xl min-h-screen bg-white shadow-md">
                <Router />
            </div>
        </div>
    );
}