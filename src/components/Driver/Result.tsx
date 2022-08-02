import Image from "next/image";
import { getOrdinal } from "../../libs/ordinal";

interface ResultProps {
  driverId: string;
  name: string;
  place: number;
  subheading?: string;
  fastestLap?: boolean;
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
  return (
    <>
      <p className="text-7xl tracking-wide text-right font-bold">
        {props.name}
      </p>
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
        <div className="basis-1/2 mt-5">
          {/* sub heading */}
          <div className="flex flex-col gap-4 h-full">
            <div>
              {props.subheading && (
                <h2 className="text-2xl font-bold text-bittersweet">
                  {props.subheading}
                </h2>
              )}
            </div>
            {/* place */}
            <div className="flex justify-center items-center grow">
              <p
                className={`text-7xl font-bold ordinal pt-4 ${getPlaceColor(
                  props.place
                )}`}
              >
                {getOrdinal(props.place)}
              </p>
            </div>

            {/* season */}
            <div className="flex flex-col w-full">
              <div className="border-b-2 border-slate-600">
                <p className="text-cyberYellow tracking-wide text-bold">
                  Season
                </p>
              </div>
              <div className="flex flex-row w-full border-b-2 border-slate-600">
                {Object.entries(props.season).map((v, idx) => {
                  return (
                    <div key={idx} className="basis-1/4">
                      <p className="capitalize text-slate-500">{v[0]}</p>
                      <p className="text-slate-200 pl-1">{v[1]}</p>
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
