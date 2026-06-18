// 입력 필드 하단 안내 메시지 (에러 / 성공)
// type='error'면 빨간색, type='success'면 초록색
export default function FieldMessage({ type = 'error', children }) {
  if (!children) return null;

  const color = type === 'success' ? 'text-green' : 'text-red';

  return <div className={`text-12-rg pl-3 ${color}`}>{children}</div>;
}
