import { GetStaticProps } from "next";
import { getConnection } from "libs/knex";

export async function getStaticPaths() {
  const knex = getConnection();
  const races = await knex({ race: "race" }).distinct("race.year");

  const paths = races.map((race) => ({
    params: { year: race.year.toString() },
  }));

  return { paths, fallback: false };
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  return {
    props: { year: params?.year },
  };
};

interface YearProps {
  year: number;
}

export default function Year({ year }: YearProps) {
  return (
    <>
      <h1>Races</h1>
      <ul className="list-disc list-inside">
        <li>
          <a className="hover:text-sky-400" href={`/races/${year}/circuits`}>
            Circuits
          </a>
        </li>
        <li>
          <a
            className="hover:text-sky-400"
            href={`/races/${year}/head-to-head`}
          >
            Head to Head
          </a>
        </li>
      </ul>
    </>
  );
}
