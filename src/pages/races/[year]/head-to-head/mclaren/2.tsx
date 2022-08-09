import Image from "next/image";
import MclarenHeader from "components/Constructor/Header/Mclaren";
import Stats from "components/Stats";
import { NorrisData, RicciardoData } from "libs/data/mclaren";

export default function Page2() {
  const showSocial = true;
  const norrisColor = "#1E88E5";
  const ricciardoColor = "#FFC107";
  return (
    <div className="w-[1200px] h-[1350px] bg-oxfordBlue text-eggshell">
      <MclarenHeader />

      <div className="px-10 mt-20">
        <p className="text-5xl tracking-wide text-bold">RICCIARDO v NORRIS</p>
        <div className="flex flex-row items-center">
          <p className="text-4xl text-bold text-cyberYellow">
            Hungarian Grand Prix 2022
          </p>
          <div className="ml-4 mt-1 border-t border-gray-400 w-4"></div>
          <p className="pl-4 text-4xl text-bold text-bittersweet">
            Fastest Lap Comparison
          </p>
        </div>
      </div>
      <div className="flex flex-row gap-10 px-10 mt-10 min-h-[500px]">
        <div className="basis-1/2">
          <div className="pt-14">
            <div className="flex flex-row pb-4 items-center">
              <p className="text-4xl text-[#1e88e5]">Norris</p>
              <div className="ml-4 mt-1 border-t border-gray-400 w-4"></div>
              <div className="pl-5 pt-1 text-2xl flex flex-row">
                <p className="text-gray-400">⏱️ 1:23.043</p>
                <p className="rounded-full ml-4 text-center bg-slate-500 w-24">
                  Lap 47
                </p>
              </div>
            </div>
            <ul className="list-disc text-xl list-inside">
              <li>Faster cornering speed than Ricciardo</li>
              <li>DRS helped on the main straight</li>
              <li>Heavier fuel load compared to Ricciardo</li>
            </ul>
          </div>
          <div className="pt-14">
            <div className="flex flex-row pb-4 items-center tracking-wide">
              <p className="text-4xl text-[#ffc107]">Ricciardo</p>
              <div className="ml-4 mt-1 border-t border-gray-400 w-4"></div>
              <div className="pl-4 pt-1 text-2xl flex flex-row">
                <p className="text-gray-400">⏱️ 1:23.590</p>
                <p className="rounded-full ml-4 text-center bg-slate-500 w-24">
                  Lap 64
                </p>
              </div>
            </div>
            <ul className="list-disc text-xl list-inside tracking-wide">
              <li>Exit speeds are normally faster than Lando</li>
              <li>Ricciardo did not have DRS during fastest lap</li>
              <li>Prefers more time on brake before turn-in</li>
            </ul>
          </div>
        </div>

        <div className="basis-1/2 pr-14">
          <div className="h-[500px] w-[540px]">
            <Stats.TrackMap
              driverData={[
                {
                  driverCode: "NOR",
                  driverColor: norrisColor,
                  data: NorrisData,
                },
                {
                  driverCode: "RIC",
                  driverColor: ricciardoColor,
                  data: RicciardoData,
                },
              ]}
            />
          </div>
        </div>
      </div>

      <div className="h-[300px] w-full pt-20 px-20">
        <Stats.CornerAnalysis
          driverData1={{
            driverCode: "NOR",
            driverColor: norrisColor,
            data: NorrisData,
          }}
          driverData2={{
            driverCode: "RIC",
            driverColor: ricciardoColor,
            data: RicciardoData,
          }}
          distanceFrom={400}
          distanceTo={850}
        />
      </div>

      <div className="pt-40 px-20"></div>

      {/* footer */}
      {showSocial && (
        <div className="flex flex-row gap-2 place-content-end mt-20 pr-14">
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
  );
}
