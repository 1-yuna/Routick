export default function HomeBannerCard({ name, image, onClick }) {
    return (
        <div className="flex justify-between h-44 mt-32 bg-primary rounded-xl overflow-hidden shadow-xl">

            <div className="flex flex-col justify-between pl-8 py-6">

                <div className="flex flex-col text-white font-bold">
                    <p>{name}님,</p>
                    <p>어디로 떠날지</p>
                    <p>정해볼까요?</p>
                </div>

                <button
                    className="w-28 h-10 bg-white text-xs text-black rounded"
                    onClick={onClick}
                >
                    코스 생성 시작
                </button>

            </div>

            <img
                className="h-full w-52 object-cover"
                src={image}
                alt="banner"
            />

        </div>
    );
}