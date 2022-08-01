import { GetStaticProps } from "next";
import { getConnection } from "../../../libs/knex";

export async function getStaticPaths() {
  const knex = getConnection();
  const races = await knex({ race: "race" }).distinct("race.year");

  // Get the paths we want to pre-render based on years
  const paths = races.map((race) => ({
    params: { year: race.year.toString() },
  }));

  // We'll pre-render only these paths at build time.
  // { fallback: false } means other routes should 404.
  return { paths, fallback: false };
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const knex = getConnection();
  const races = await knex
    .select({
      year: "race.year",
      date: "race.date",
      round: "race.round_number",
      name: "circuit.name",
      country: "circuit.country",
      circuitId: "circuit.circuit_id",
      id: "race.id",
    })
    .from("race")
    .join("circuit", { "circuit.circuit_id": "race.circuit_id" })
    .where("race.year", params?.year);

  return {
    props: { races },
  };
};

interface YearProps {
  races: Array<{
    id: number;
    year: number;
    date: Date;
    round: number;
    name: string;
    country: string;
    circuitId: string;
  }>;
}

export default function Year({ races }: YearProps) {
  return (
    <>
      <h1>Races</h1>
      <ul className="list-disc list-inside">
        {races.map((r) => (
          <li key={r.year}>
            <a
              className="hover:text-sky-400"
              href={`/races/${r.year}/${r.circuitId}`}
            >
              {r.country} - {r.name} - {r.date}
            </a>
          </li>
        ))}
      </ul>
    </>
  );
}
