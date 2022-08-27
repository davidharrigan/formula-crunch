import Image from "next/image";
import { getOrdinal } from "../../libs/ordinal";
import {
  ChevronDoubleUpIcon,
  ChevronDoubleDownIcon,
} from "@heroicons/react/solid";

interface ResultProps {
  driverId: string;
  name: string;
  place: number;
  year: number;
  status?: string;
  gridPosition: number;
  subheading?: string;
  fastestLap?: boolean;
  lapsCompleted: number;
  season: {
    rank: number;
    points: number;
    wins: number;
    podiums: number;
  };
}

const getPlaceColor = (place: number): string => {
  if (place === 1) {
    return "text-gold";
  }
  if (place === 2) {
    return "text-silver";
  }
  if (place === 3) {
    return "text-bronze";
  }
  return "text-neutral";
};

const Result = (props: ResultProps) => {
  const positionGained = props.gridPosition - props.place;
  const finishedRace =
    !props.status ||
    props.status === "Finished" ||
    props.status?.includes("Lap");
  const status = finishedRace ? undefined : "DNF";

  return (
    <>
      <div className="pl-10">
        <p className="text-6xl tracking-wide font-bold">{props.name}</p>
      </div>
      {props.subheading && (
        <p className="text-3xl font-bold text-bittersweet text-right">
          {props.subheading}
        </p>
      )}

      <div className="flex flex-row">
        {/* left column */}
        <div className="basis-1/2">
          <Image
            src={`/drivers/${props.driverId}.png`}
            alt={props.name}
            width={300}
            height={300}
          />
        </div>

        {/* right column */}
        <div className="basis-1/2 mt-10">
          <div className="flex flex-col justify-between h-full">
            {/* place */}
            <div className="flex flex-row">
              <div className="basis-2/3">
                <div className="flex justify-center items-center grow">
                  <p
                    className={`text-8xl font-bold ordinal pt-4 ${getPlaceColor(
                      props.place
                    )}`}
                  >
                    {getOrdinal(props.place)}
                  </p>
                </div>
              </div>
              <div className="basis-1/3 items-center text-center self-center pt-4">
                <div className="font-bold text-4xl">
                  {positionGained >= 0 && (
                    <p className="text-emerald-500">
                      <ChevronDoubleUpIcon className="inline-block h-10 w-10 pb-1 pr-1" />
                      {positionGained}
                    </p>
                  )}
                  {positionGained < 0 && (
                    <p className="text-red-500">
                      <ChevronDoubleDownIcon className="inline-block h-10 w-10 pb-1 pr-1" />
                      {positionGained * -1}
                    </p>
                  )}
                </div>
                <p className="text-slate-500 font-bold">
                  Started{" "}
                  <span className="ordinal">
                    {getOrdinal(props.gridPosition)}
                  </span>
                </p>
              </div>
            </div>

            <div className="self-center flex flex-row gap-3">
              <p className="rounded-full text-center bg-slate-500 w-24">
                {props.lapsCompleted} Laps
              </p>
              {status && (
                <p className="rounded-full text-center bg-red-500 ring-red-200 w-24">
                  {status}
                </p>
              )}
            </div>

            {/* season */}
            <div className="flex flex-col w-full">
              <div className="border-b-2 border-slate-600">
                <p className="text-cyberYellow tracking-wide text-bold text-2xl">
                  Season {props.year}
                </p>
              </div>
              <div className="flex flex-row w-full border-b-2 border-slate-600">
                {Object.entries(props.season).map((v, idx) => {
                  return (
                    <div key={idx} className="basis-1/4">
                      <p className="capitalize text-slate-500 text-xl">
                        {v[0]}
                      </p>
                      <p className="text-slate-200 pl-1 text-bold text-3xl">
                        {v[1]}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Result;
