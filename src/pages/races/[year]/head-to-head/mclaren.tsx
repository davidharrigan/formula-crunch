import Image from "next/image";
import Driver from "components/Driver";
import MclarenHeader from "components/Constructor/Header/Mclaren";
import Stats from "components/Stats";

export default function MclarenHeadToHead() {
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
              value: 19,
            }}
            driver2={{
              code: "NOR",
              value: 76,
            }}
            leader={{
              code: "VER",
              value: 258,
            }}
          />
          <Stats.ThreeBars
            title="Average Finish"
            inverse={true}
            worst={20}
            driver1={{
              code: "RIC",
              value: 12.15,
            }}
            driver2={{
              code: "NOR",
              value: 8.77,
            }}
            leader={{
              code: "VER",
              value: 1,
            }}
          />
          <Stats.ThreeBars
            title="Average Grid"
            inverse={true}
            worst={0}
            driver1={{
              code: "RIC",
              value: 30,
            }}
            driver2={{
              code: "NOR",
              value: 70,
            }}
            leader={{
              code: "VER",
              value: 100,
            }}
          />
          <Stats.ThreeBars
            title="Average Positions Gained"
            inverse={true}
            worst={0}
            driver1={{
              code: "RIC",
              value: 30,
            }}
            driver2={{
              code: "NOR",
              value: 70,
            }}
            leader={{
              code: "VER",
              value: 100,
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
