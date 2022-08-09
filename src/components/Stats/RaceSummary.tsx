import { getOrdinal } from "../../libs/ordinal";
import Card from "./Card";
import Tire from "./Tire";

interface RaceSummaryProps {
  startingGrid: number;
  time: string;
  tires: {
    compound: "soft" | "medium" | "hard";
    laps: number;
  }[];
}

export const RaceSummary = ({
  startingGrid,
  time,
  tires,
}: RaceSummaryProps) => {
  return (
    <div className="flex flex-col gap-10">
      <div className="grid grid-cols-2 gap-4 grid-flow-row">
        <Card title="Starting Grid" value={getOrdinal(startingGrid)} />
        <Card title="Time" value={time} />
      </div>
      <div className="flex flex-col gap-4">
        <div>
          <p className="text-xl tracking-wide font-bold text-oldLavender">
            Tyres
          </p>
        </div>
        <div className="flex flex-cols gap-6 items-end">
          {tires.map((t, idx) => (
            <Tire key={idx} compound={t.compound} laps={t.laps} />
          ))}
        </div>
      </div>
    </div>
  );
};
