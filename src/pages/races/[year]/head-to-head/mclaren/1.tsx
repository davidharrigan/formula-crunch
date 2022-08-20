import Image from "next/image";
import Driver from "components/Driver";
import MclarenHeader from "components/Constructor/Header/Mclaren";
import Stats from "components/Stats";

interface HeadToHeadProps {
  drivers: {
    driverId: string;
    gridPosition: number;
    position: number;
    year: number;
    date: string;
    points: number;
  }[];
}

export default function MclarenHeadToHead(props: HeadToHeadProps) {
  // 2022-08-07
  const showSocial = true;
  return (
    <div className="w-[1200px] h-[1350px] bg-oxfordBlue text-eggshell">
      <MclarenHeader />
      <div className="flex flex-col gap-10">
        <div className="flex flex-row relative">
          <p className="text-6xl absolute left-1/2 top-1/2 w-20 -ml-10 pt-8 text-bittersweet font-serif">
            VS
          </p>
          <div className="basis-1/2 pt-4">
            <Driver.Profile
              driverId="ricciardo"
              firstName="Daniel"
              lastName="Ricciardo"
              rank={12}
            />
          </div>
          <div className="basis-1/2 pt-4">
            <Driver.Profile
              driverId="norris"
              firstName="Lando"
              lastName="Norris"
              rank={7}
            />
          </div>
        </div>

        {/*stats */}
        <div className="flex flex-col pt-4 px-16 gap-16">
          <Stats.ThreeBars
            title="Points"
            inverse={false}
            worst={0}
            driver1={{
              code: "RIC",
              value: 16,
              rank: 12,
            }}
            driver2={{
              code: "NOR",
              value: 72,
              rank: 7,
            }}
            leader={{
              code: "VER",
              value: 258,
            }}
          />
        </div>

        <div className="flex flex-col pt-4 px-16 gap-16">
          <Stats.ThreeBars
            title="Average Finish (Race)"
            inverse={true}
            worst={16}
            driver1={{
              code: "RIC",
              value: 12.15,
              rank: 13,
            }}
            driver2={{
              code: "NOR",
              value: 8.77,
              rank: 7,
            }}
            leader={{
              code: "VER",
              value: 4.38,
            }}
          />
        </div>

        <div className="flex flex-col pt-4 px-16 gap-16">
          <Stats.ThreeBars
            title="Average Grid (Race)"
            inverse={true}
            worst={16}
            driver1={{
              code: "RIC",
              value: 11.23,
              rank: 12,
            }}
            driver2={{
              code: "NOR",
              value: 8.23,
              rank: 7,
            }}
            leader={{
              code: "VER",
              value: 2.85,
            }}
          />
        </div>

        <div className="flex flex-col pt-4 px-16 gap-16">
          <Stats.ThreeBars
            title="Average Positions Gained (Race)"
            inverse={false}
            worst={-4}
            driver1={{
              code: "RIC",
              value: -0.92,
              rank: 12,
            }}
            driver2={{
              code: "NOR",
              value: -0.54,
              rank: 10,
            }}
            leader={{
              code: "STR",
              value: 3.15,
            }}
          />
        </div>

        {/* footer */}
        {showSocial && (
          <div className="flex flex-row gap-2 place-content-end mt-4 pr-14">
            <Image
              src="/social/twitter.svg"
              alt="twitter-icon"
              width={24}
              height={24}
            />
            <Image
              src="/social/instagram.svg"
              alt="twitter-icon"
              width={24}
              height={24}
            />
            <p className="text-2xl font-thin">@formula_crunch</p>
          </div>
        )}
      </div>
    </div>
  );
}
