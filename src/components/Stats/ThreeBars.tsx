import { getOrdinal } from "libs/ordinal";

interface Driver {
  code: string;
  value: number;
  rank?: number;
}

interface ThreeBarsProps {
  worst: number;
  inverse: boolean;
  title: string;
  driver1: Driver;
  driver2: Driver;
  leader: Driver;
}

const ThreeBars = ({
  title,
  driver1,
  driver2,
  leader,
  worst = 0,
  inverse = false,
}: ThreeBarsProps) => {
  const drivers = [driver1, driver2, leader];

  let max = leader.value;
  let driver1Value = driver1.value;
  let driver2Value = driver2.value;
  if (worst < 0) {
    driver1Value += -worst;
    driver2Value += -worst;
    max += -worst;
    worst = 0;
  }

  const driver1Perc = inverse
    ? ((worst - driver1Value) / (worst - 1)) * 100
    : (driver1Value / max) * 100;

  const driver2Perc = inverse
    ? ((worst - driver2Value) / (worst - 1)) * 100
    : (driver2Value / max) * 100;

  return (
    <div className="w-100">
      <div className="pb-3 text-cyberYellow text-4xl">{title}</div>
      <div className="flex flex-row">
        <div className="flex flex-col">
          {drivers.map((d) => {
            return (
              <div className="text-3xl tracking-widest font-mono">{d.code}</div>
            );
          })}
        </div>
        <div className="flex flex-col grow px-6">
          <div
            className={`h-full ${
              driver1Perc > driver2Perc ? "bg-emerald-500" : "bg-rose-500"
            }`}
            style={{ width: `${driver1Perc}%` }}
          >
            <p className="ordinal text-right text-xl pr-4 pt-0.5">
              {driver1.rank && getOrdinal(driver1.rank)}
            </p>
          </div>
          <div
            className={`h-full ${
              driver2Perc > driver1Perc ? "bg-emerald-500" : "bg-rose-500"
            }`}
            style={{ width: `${driver2Perc}%` }}
          >
            <p className="ordinal text-right text-xl pr-4 pt-0.5">
              {driver2.rank && getOrdinal(driver2.rank)}
            </p>
          </div>
          <div className="bg-gray-500 h-full w-full">
            <p className="text-xl text-right pr-4 pt-0.5">Leader</p>
          </div>
        </div>
        <div className="flex flex-col text-right">
          {drivers.map((d) => {
            return <div className="text-3xl tracking-wide">{d.value}</div>;
          })}
        </div>
      </div>
    </div>
  );
};

export default ThreeBars;
