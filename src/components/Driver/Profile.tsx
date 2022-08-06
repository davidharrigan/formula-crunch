import Image from "next/image";
import { getOrdinal } from "libs/ordinal";

interface ProfileProps {
  driverId: string;
  firstName: string;
  lastName: string;
  rank: number;
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

const Result = (props: ProfileProps) => {
  return (
    <>
      <div className="flex flex-row">
        <div className="basis-1/2">
          <Image
            src={`/drivers/${props.driverId}.png`}
            alt={`${props.firstName} ${props.lastName}`}
            width={300}
            height={300}
          />
        </div>

        <div className="basis-1/2 mt-10">
          <div>
            <p
              className={`text-6xl -ml-10 tracking-wide font-bold text-mclaren`}
            >
              {props.firstName}
            </p>
            <p className="text-6xl tracking-wide font-bold">{props.lastName}</p>
          </div>

          <div className="flex flex-col justify-between h-full">
            {/* place */}
            <div className="flex flex-row">
              <div className="flex">
                <p
                  className={`text-8xl font-bold ordinal pl-10 pt-6 ${getPlaceColor(
                    props.rank
                  )}`}
                >
                  {getOrdinal(props.rank)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Result;
