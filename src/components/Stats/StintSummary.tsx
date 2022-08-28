import Tire from "./Tire";

interface StintSummaryProps {
  stints: {
    compound: "SOFT" | "MEDIUM" | "HARD" | "WET" | "INTERMEDIATE";
    lapCount: number;
    averageTime: string;
  }[];
}

export const StintSummary = (props: StintSummaryProps) => {
  return (
    <div className="flex flex-col gap-3 w-full h-full">
      <div className="flex flex-row w-full font-bold text-3xl tracking-wide pb-1">
        <div className="basis-1/5 text-oldLavender">Stint</div>
        <div className="basis-2/5 text-oldLavender">Pace</div>
        <div className="basis-2/5 text-oldLavender">Laps</div>
      </div>
      {props.stints.map((s, idx) => {
        return (
          <div className="flex flex-row w-full font-bold text-3xl" key={idx}>
            <div className="basis-1/5">
              <Tire compound={s.compound} height={50} width={50} />
            </div>
            <div className="basis-2/5 pt-1">{s.averageTime}</div>
            <div className="basis-2/5 pt-1">{s.lapCount}</div>
          </div>
        );
      })}
    </div>
  );
};
