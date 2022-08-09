import {
  ResponsiveContainer,
  LineChart,
  XAxis,
  YAxis,
  Line,
  CartesianGrid,
} from "recharts";
import { ArrowNarrowRightIcon } from "@heroicons/react/solid";

interface DriverData {
  driverCode: string;
  driverColor: string;
  data: Telemetry[];
}

interface Telemetry {
  X: number;
  Y: number;
  Speed: number;
  Distance: number;
  Brake: boolean;
  Throttle: number;
}

interface CornerAnalysisProps {
  driverData1: DriverData;
  driverData2: DriverData;
  distanceFrom: number;
  distanceTo: number;
}

const getData = (
  distanceFrom: number,
  distanceTo: number,
  driverData: DriverData[]
) => {
  const data: any[] = [];

  driverData.forEach((driver, d_idx) => {
    const driverCode = driver.driverCode;
    for (let i = 0; i < driver.data.length; i++) {
      const {
        Distance: distance,
        Speed: speed,
        Brake: brake,
        Throttle: throttle,
      } = driver.data[i];

      if (distance >= distanceFrom) {
        let currentAction = "";
        if (brake) currentAction = "brake";
        else if (throttle >= 99) currentAction = "full_throttle";
        else if (!brake && throttle < 99) currentAction = "cornering";

        const actionValue = d_idx * 40;
        const row = {
          distance: distance - distanceFrom,
          [`${driverCode}_speed`]: speed,
          [`${driverCode}_brake`]: brake,
          [`${driverCode}_throttle`]: throttle,
          [`${driverCode}_action_brake`]:
            currentAction === "brake" ? actionValue : null,
          [`${driverCode}_action_full_throttle`]:
            currentAction === "full_throttle" ? actionValue : null,
          [`${driverCode}_action_cornering`]:
            currentAction === "cornering" ? actionValue : null,
        };
        data.push(row);
      }
      if (distance > distanceTo) {
        break;
      }
    }
  });
  return data;
};

export const CornerAnalysis = (props: CornerAnalysisProps) => {
  const data = getData(props.distanceFrom, props.distanceTo, [
    props.driverData1,
    props.driverData2,
  ]);

  data.push(
    ...[
      {
        distance: 0,
      },
      {
        distance: 100,
      },
      {
        distance: 200,
      },
      {
        distance: 300,
      },
      {
        distance: 400,
      },
    ]
  );

  const colors = {
    brake: "#FBBF24",
    fullThrottle: "#34D399",
    cornering: "#A1A1AA",
  };

  // TODO: remove hard coded stuff here (turn / driver)

  return (
    <div className="w-full h-full">
      <div className="bg-oldLavender">
        <p className="text-3xl px-5 py-2 mb-5 tracking-wider">
          Corner Analysis - Turn 1
        </p>
      </div>
      <div className="flex flex-row h-full">
        <div className="basis-1/4 relative">
          <div className="pt-3">
            <p className="text-xl">Speed (km/h)</p>
          </div>
          <div className="absolute bottom-4 left-0 w-full">
            <div className="flex flex-row w-full">
              <div
                className="w-6"
                style={{ background: props.driverData1.driverColor }}
              ></div>
              <p className="pl-2 text-lg text-bold tracking-wider">NORRIS</p>
              <div className="flex grow justify-end">
                <ArrowNarrowRightIcon width={28} height={28} />
              </div>
            </div>
            <div className="flex flex-row mt-2 w-full">
              <div
                className="w-6"
                style={{ background: props.driverData2.driverColor }}
              ></div>
              <p className="pl-2 text-lg text-bold tracking-wider">RICCIARDO</p>
              <div className="flex grow justify-end">
                <ArrowNarrowRightIcon width={28} height={28} />
              </div>
            </div>
          </div>
        </div>
        <div className="basis-3/4 h-full">
          <ResponsiveContainer>
            <LineChart data={data} margin={{ left: -10, right: 70 }}>
              <XAxis
                type="number"
                dataKey="distance"
                scale="linear"
                tick={true}
                axisLine={true}
                tickCount={3}
                allowDecimals={false}
                domain={[0, props.distanceTo - props.distanceFrom]}
              />
              <YAxis />
              <CartesianGrid strokeDasharray="3" />
              {[props.driverData1, props.driverData2].map((d) => {
                return (
                  <Line
                    key={d.driverCode}
                    strokeWidth={2}
                    type="monotone"
                    dataKey={`${d.driverCode}_speed`}
                    dot={false}
                    stroke={d.driverColor}
                  />
                );
              })}

              {[props.driverData1, props.driverData2].map((d) => {
                return (
                  <>
                    <Line
                      key={`${d.driverCode}-conering`}
                      strokeWidth={10}
                      dot={false}
                      dataKey={`${d.driverCode}_action_cornering`}
                      stroke={colors["cornering"]}
                    />
                    <Line
                      key={`${d.driverCode}-full-throttle`}
                      strokeWidth={10}
                      dot={false}
                      dataKey={`${d.driverCode}_action_full_throttle`}
                      stroke={colors["fullThrottle"]}
                    />
                    <Line
                      key={`${d.driverCode}-brake`}
                      dot={false}
                      strokeWidth={10}
                      dataKey={`${d.driverCode}_action_brake`}
                      stroke={colors["brake"]}
                    />
                  </>
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="flex flex-col items-center">
        <div className="pl-72">Distance (meters)</div>
        <div className="pl-72 flex flex-row items-center gap-10">
          <div className="flex flex-row">
            <div className="border-t-8 mt-2 border-amber-400 w-4"></div>
            <p className="pl-2">Braking</p>
          </div>
          <div className="flex flex-row">
            <div className="border-t-8 mt-2 border-emerald-400 w-4"></div>
            <p className="pl-2">Full Throttle</p>
          </div>
          <div className="flex flex-row">
            <div className="border-t-8 mt-2 border-zinc-400 w-4"></div>
            <p className="pl-2">Cornering</p>
          </div>
        </div>
      </div>
    </div>
  );
};
