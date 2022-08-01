import { GetStaticProps } from "next";
import { getConnection } from "../../libs/knex";

export const getStaticProps: GetStaticProps = async () => {
  const knex = getConnection();
  const races = await knex({ race: "race" }).distinct("race.year");
  return {
    props: { races },
  };
};

interface YearsProps {
  races: Array<{ year: number }>;
}

export default function Years({ races }: YearsProps) {
  return (
    <>
      <h1>Years</h1>
      <ul className="list-disc list-inside">
        {races.map((r) => (
          <li key={r.year}>
            <a className="hover:text-sky-400" href={`/races/${r.year}`}>
              {r.year}
            </a>
          </li>
        ))}
      </ul>
    </>
  );
}
