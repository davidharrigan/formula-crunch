interface Driver {
  code: string;
  value: number;
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
  const max = leader.value;

  const driver1Perc = inverse
    ? ((worst - driver1.value) / (worst - 1)) * 100
    : (driver1.value / max) * 100;

  const driver2Perc = inverse
    ? ((worst - driver2.value) / (worst - 1)) * 100
    : (driver2.value / max) * 100;

  console.log(driver1Perc);
  console.log(driver2Perc);

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
            &nbsp;
          </div>
          <div
            className={`h-full ${
              driver2Perc > driver1Perc ? "bg-emerald-500" : "bg-rose-500"
            }`}
            style={{ width: `${driver2Perc}%` }}
          >
            &nbsp;
          </div>
          <div className="bg-gray-500 h-full w-full">&nbsp;</div>
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
