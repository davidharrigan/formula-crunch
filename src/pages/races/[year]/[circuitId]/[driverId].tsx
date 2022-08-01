import { GetStaticProps } from "next";
import { getConnection } from "../../../../libs/knex";

import Driver from "../../../../components/Driver";
import Stats from "../../../../components/Stats";

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
  const knex = getConnection();
  const raceSummary = await knex
    .select({
      driverId: "driver_race_summary.driver_id",
      raceSummaryId: "driver_race_summary.id",
      raceId: "driver_race_summary.race_id",
    })
    .from("driver_race_summary")
    .where({
      "driver_race_summary.driver_id": params?.driverId,
      "race.circuit_id": params?.circuitId,
      "race.year": params?.year,
    })
    .join("race", { "race.id": "driver_race_summary.race_id" })
    .first();

  const race = await knex
    .select({
      year: "year",
      roundNumber: "round_number",
    })
    .from("race")
    .where({
      id: raceSummary.raceId,
    })
    .first();

  const driver = await knex
    .select({
      driverId: "driver_id",
      code: "code",
      firstName: "first_name",
      lastName: "last_name",
    })
    .from("driver")
    .where({ driverId: raceSummary.driverId })
    .first();

  return {
    props: { race, driver },
  };
};

interface DriverRaceSummaryProps {
  driver: {
    driverId: string;
    firstName: string;
    lastName: string;
  };
  race: {
    year: number;
    roundNumber: number;
  };
}

export default function Year({ driver, race }: DriverRaceSummaryProps) {
  return (
    <div className="w-[1200px] h-[1200px] p-5 bg-oxfordBlue text-eggshell">
      <div className="flex flex-col gap-10">
        <div className="flex flex-row">
          <div className="basis-1/2">
            <Driver.Result
              name={`${driver.firstName} ${driver.lastName}`}
              subheading={`${race.year} TODO`}
              place={2}
              image={`drivers/${driver.driverId}.png`}
              season={{ rank: 1, points: 208, wins: 6, podiums: 8 }}
            />
          </div>
          <div className="basis-1/2 px-16 mt-24">
            <Stats.RaceSummary
              startingGrid={1}
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
            value="1:07.275"
            subtext="Lap 62"
            rank={1}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Pace"
            value="1:07.275"
            rank={2}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Pit"
            value="21.319"
            subtext="Lap 58"
            rank={4}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Total Pit Time"
            value="1:04:785"
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Overtakes"
            value="1"
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Speed"
            value="217.777"
            subtext="kmh"
            rank={3}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Speed Trap"
            value="325.5"
            subtext="kmh"
            rank={2}
            totalParticipants={20}
          />
        </div>
      </div>
    </div>
  );
}
