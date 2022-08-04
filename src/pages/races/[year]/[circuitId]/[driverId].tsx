import { GetStaticProps } from "next";
import { getConnection } from "../../../../libs/knex";
import Image from "next/image";

import Driver from "../../../../components/Driver";
import Stats from "../../../../components/Stats";
import {
  getRace,
  getDriver,
  getLapSummary,
  getRaceSummary,
  getPitSummary,
  getOvertakeSummary,
} from "../../../../libs/db";
import type {
  Driver as DriverType,
  LapSummary,
  RaceSummary,
  Race,
  PitSummary,
  OvertakeSummary,
} from "../../../../libs/db";

interface DriverRaceSummaryProps {
  driver: DriverType;
  race: Race;
  raceSummary: RaceSummary;
  lapSummary: LapSummary;
  pitSummary: PitSummary;
  overtakeSummary: OvertakeSummary;
}

const TOTAL_PARTICIPANTS = 20;

export async function getStaticPaths() {
  const knex = getConnection();
  const drivers = await knex
    .select({
      circuitId: "race.circuit_id",
      driverId: "driver_race_summary.driver_id",
      year: "race.year",
    })
    .from("driver_race_summary")
    .join("race", { "race.id": "driver_race_summary.race_id" });

  // Get the paths we want to pre-render based on years
  const paths = drivers.map((driver) => ({
    params: {
      year: driver.year.toString(),
      circuitId: driver.circuitId,
      driverId: driver.driverId,
    },
  }));

  // We'll pre-render only these paths at build time.
  // { fallback: false } means other routes should 404.
  return { paths, fallback: false };
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  if (!(params?.driverId && params?.circuitId && params?.year)) {
    return {
      notFound: true,
    };
  }

  const knex = getConnection();

  const raceSummary = await getRaceSummary(
    knex,
    params.driverId as string,
    params.circuitId as string,
    params.year as string
  );
  if (!raceSummary) {
    return {
      notFound: true,
    };
  }

  const [race, driver, lapSummary, pitSummary, overtakeSummary] =
    await Promise.all([
      getRace(knex, raceSummary.raceId),
      getDriver(knex, raceSummary.driverId),
      getLapSummary(knex, raceSummary.raceId, raceSummary.id),
      getPitSummary(knex, raceSummary.raceId, raceSummary.id),
      getOvertakeSummary(knex, raceSummary.raceId, raceSummary.id),
    ]);

  return {
    props: {
      raceSummary,
      race,
      driver,
      lapSummary,
      pitSummary,
      overtakeSummary,
    },
  };
};

export default function DriverRace({
  raceSummary,
  driver,
  race,
  lapSummary,
  pitSummary,
  overtakeSummary,
}: DriverRaceSummaryProps) {
  const showSocial = true;
  return (
    <div className="w-[1200px] h-[1200px] p-4 bg-oxfordBlue text-eggshell">
      <div className="flex flex-col gap-10">
        <div className="flex flex-row">
          <div className="basis-1/2 pt-4">
            <Driver.Result
              name={`${driver.firstName} ${driver.lastName}`}
              subheading={race.eventName}
              place={raceSummary.position}
              gridPosition={raceSummary.gridPosition}
              year={race.year}
              driverId={driver.driverId}
              season={{
                rank: raceSummary.seasonStanding,
                points: raceSummary.seasonPoints,
                wins: raceSummary.wins,
                podiums: raceSummary.podiums,
              }}
              status={raceSummary.status}
              lapsCompleted={raceSummary.lapsCompleted}
            />
          </div>
          <div className="basis-1/2 p-3 mt-16">
            <p className="pl-8 text-bold text-cyberYellow text-2xl">
              Fastest Lap Gear Shifts
            </p>
            <div>
              <Image
                src={`/gear-plots/${race.year}/${race.circuitId}/${driver.driverId}.svg`}
                alt={`Gear shifts ${race.year} ${race.eventName} ${driver.driverId}`}
                width={560}
                height={350}
              />
            </div>
          </div>
        </div>

        {/* sliders */}
        <div className="grid px-16 grid-cols-2 gap-y-20 gap-x-16">
          <Stats.Slider
            name="Fastest Lap"
            value={lapSummary.fastestLapTime}
            subtext={`Lap ${lapSummary.fastestLap}`}
            rank={lapSummary.fastestLapRank}
            totalParticipants={TOTAL_PARTICIPANTS}
          />
          <Stats.Slider
            name="Average Pace"
            value={lapSummary.averageTime}
            rank={lapSummary.averageTimeRank}
            totalParticipants={TOTAL_PARTICIPANTS}
          />
          <Stats.Slider
            name="Fastest Pit"
            value={pitSummary?.fastestPitTime ?? "N/A"}
            subtext={pitSummary ? `Lap ${pitSummary.fastestPitLap}` : undefined}
            rank={pitSummary?.fastestPitRank ?? TOTAL_PARTICIPANTS}
            totalParticipants={TOTAL_PARTICIPANTS}
          />
          <Stats.Slider
            name="Total Pit Time"
            value={pitSummary?.totalTime ?? "N/A"}
            rank={pitSummary?.totalTimeRank ?? TOTAL_PARTICIPANTS}
            subtext={
              pitSummary
                ? `${pitSummary.totalStops} ${
                    pitSummary.totalStops > 1 ? "Stops" : "Stop"
                  }`
                : undefined
            }
            totalParticipants={TOTAL_PARTICIPANTS}
          />
          <Stats.Slider
            name="Overtakes"
            value={overtakeSummary.overtakes}
            rank={overtakeSummary.overtakesRank ?? TOTAL_PARTICIPANTS}
            totalParticipants={TOTAL_PARTICIPANTS}
          />
          <Stats.Slider
            name="Average Speed"
            value={lapSummary.averageSpeed}
            subtext="kmh"
            rank={lapSummary.averageSpeedRank}
            totalParticipants={TOTAL_PARTICIPANTS}
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
