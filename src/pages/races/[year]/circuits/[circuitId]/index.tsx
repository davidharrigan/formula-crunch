import { GetStaticProps } from "next";
import { getConnection } from "libs/knex";

export async function getStaticPaths() {
  const knex = getConnection();
  const races = await knex
    .select({ year: "race.year", circuitId: "race.circuit_id" })
    .from("race");

  const paths = races.map((race) => ({
    params: { year: race.year.toString(), circuitId: race.circuitId },
  }));
  return { paths, fallback: false };
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const knex = getConnection();
  const summaries = await knex
    .select({
      driverRaceSummaryId: "driver_race_summary.id",
      firstName: "driver.first_name",
      lastName: "driver.last_name",
      code: "driver.code",
      driverId: "driver.driver_id",
    })
    .from("driver_race_summary")
    .join("driver", { "driver.driver_id": "driver_race_summary.driver_id" })
    .join("race", { "race.id": "driver_race_summary.race_id" })
    .where({ "race.year": params?.year, "race.circuit_id": params?.circuitId });

  return {
    props: { summaries, year: params?.year, circuitId: params?.circuitId },
  };
};

interface DriversProps {
  year: number;
  circuitId: string;
  summaries: Array<{
    driverRaceSummaryId: number;
    driverId: string;
    firstName: string;
    lastName: string;
    code: string;
  }>;
}

export default function Drivers({ summaries, year, circuitId }: DriversProps) {
  return (
    <>
      <h1>Races</h1>
      <ul className="list-disc list-inside">
        {summaries.map((s) => (
          <li key={s.driverRaceSummaryId}>
            <a
              className="hover:text-sky-400"
              href={`/races/${year}/circuits/${circuitId}/drivers/${s.driverId}`}
            >
              {s.firstName} {s.lastName}
            </a>
          </li>
        ))}
      </ul>
    </>
  );
}
