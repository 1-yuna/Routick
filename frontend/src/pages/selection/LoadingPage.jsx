import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import logo from '../../assets/images/logo.png';
import useSelectionStore from '../../store/selectionStore.jsx';
import useCourseStore from '../../store/courseStore.jsx';
import { savePreferences, generateCourse } from '../../api/course.jsx';
import { buildPreferencePayload } from '../../utils/preferenceUtils.jsx';
import { normalizeCourse } from '../../utils/courseUtils.jsx';

export default function LoadingPage() {
  const navigate = useNavigate();
  const setCourse = useCourseStore((state) => state.setCourse);
  const requested = useRef(false);
  const [progress, setProgress] = useState(0);

  // 90%까지는 서서히(점점 느려지며) 채우고, 실제 응답 오기 전까진 거기서 대기
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 90 ? prev : prev + (90 - prev) * 0.05));
    }, 200);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (requested.current) return;
    requested.current = true;

    (async () => {
      try {
        const payload = buildPreferencePayload(useSelectionStore.getState());
        const prefRes = await savePreferences(payload);
        const { preferenceId } = prefRes.data.data;

        const courseRes = await generateCourse(preferenceId);
        setCourse(normalizeCourse(courseRes.data.data));

        setProgress(100);
        setTimeout(() => navigate('/result'), 400);
      } catch (e) {
        navigate('/fail');
      }
    })();
  }, [navigate, setCourse]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-white gap-16">
      <img src={logo} alt="Routick" className="w-40 object-contain" />

      <div className="flex flex-col items-center gap-3 w-full px-12">
        <div className="w-full h-1 bg-line1 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-14-rg text-gray2">
          딱 맞는 여행 코스를 찾고있어요✈️
        </p>
      </div>
    </div>
  );
}
