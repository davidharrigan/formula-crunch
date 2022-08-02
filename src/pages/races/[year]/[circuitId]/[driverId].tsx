import { GetStaticProps } from "next";
import { getConnection } from "../../../../libs/knex";

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
      getLapSummary(knex, raceSummary.id),
      getPitSummary(knex, raceSummary.id),
      getOvertakeSummary(knex, raceSummary.id),
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
  return (
    <div className="w-[1200px] h-[1200px] p-5 bg-oxfordBlue text-eggshell">
      <div className="flex flex-col gap-10">
        <div className="flex flex-row">
          <div className="basis-1/2">
            <Driver.Result
              name={`${driver.firstName} ${driver.lastName}`}
              subheading={`${race.year} ${race.eventName}`}
              place={raceSummary.position}
              image={`drivers/${driver.driverId}.png`}
              season={{
                rank: raceSummary.seasonStanding,
                points: raceSummary.seasonPoints,
                wins: 0,
                podiums: 0,
              }}
            />
          </div>
          <div className="basis-1/2 px-16 mt-24">
            <Stats.RaceSummary
              startingGrid={raceSummary.gridPosition}
              time="1:24:25:844"
              tires={[
                { compound: "hard", laps: 22 },
                { compound: "hard", laps: 23 },
                { compound: "medium", laps: 13 },
              ]}
            />
          </div>
        </div>

        <div className="grid pt-4 px-16 grid-cols-2 gap-16">
          <Stats.Slider
            name="Fastest Lap"
            value={lapSummary.fastestLapTime}
            subtext={`Lap ${lapSummary.fastestLap}`}
            rank={1}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Pace"
            value={lapSummary.averageTime}
            rank={2}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Pit"
            value={pitSummary.fastestPitTime}
            subtext={`Lap ${pitSummary.fastestPitLap}`}
            rank={4}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Total Pit Time"
            value={pitSummary.totalTime}
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Overtakes"
            value={overtakeSummary.numberOvertakes}
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Speed"
            value={lapSummary.averageSpeed}
            subtext="kmh"
            rank={3}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Speed Trap"
            value={lapSummary.fastestSpeedTrap}
            subtext="kmh"
            rank={2}
            totalParticipants={20}
          />
        </div>
      </div>
    </div>
  );
}
