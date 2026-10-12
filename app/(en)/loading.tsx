export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="animate-pulse flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-primary-200" />
        <div className="h-4 w-48 bg-neutral-200 rounded" />
      </div>
    </div>
  );
}
