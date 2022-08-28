import { ClockIcon } from "@heroicons/react/solid";

interface TotalTimeProps {
  time: string;
  status: string;
}

export const TotalTime = ({ time, status }: TotalTimeProps) => {
  const display = time
    ? time
    : status.toLocaleLowerCase().includes("lap")
    ? status
    : "";

  return (
    <div className="flex flex-row text-3xl font-bold gap-4">
      {display && (
        <>
          <p className="">
            <ClockIcon className="inline-block h-10 w-10 pb-1 pr-1" />
            Total Time
          </p>
          <p className="w-8 border-t-2 mt-5 border-oldLavender"></p>
          <p className="text-cyberYellow">{display}</p>
        </>
      )}
    </div>
  );
};
