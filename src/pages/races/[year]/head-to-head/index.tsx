export default function HeadToHead() {
  return (
    <>
      <h1>Races</h1>
      <ul className="list-disc list-inside">
        <li>
          <a
            className="hover:text-sky-400"
            href={`/races/2022/head-to-head/mclaren`}
          >
            Mclaren
          </a>
        </li>
      </ul>
    </>
  );
}
