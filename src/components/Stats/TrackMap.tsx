import {
  Legend,
  ResponsiveContainer,
  LineChart,
  XAxis,
  YAxis,
  Line,
  Tooltip,
} from "recharts";

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
}

interface TrackMapProps {
  driverData: DriverData[];
}

export const TrackMap = ({ driverData }: TrackMapProps) => {
  // TODO: ensure only two drivers
  // TODO: x/y domain
  const trackColor = "#f1e9da";

  const getSpeedAtDistance = (distance: number, data: Telemetry[]): number => {
    for (let i = 1; i < data.length; i++) {
      if (data[i].Distance >= distance) {
        // TODO: need to interpolate distance...?
        return data[i].Speed;
      }
    }
    return 0;
  };

  const pickFastest = (driverData: DriverData[]) => {
    const fastest = driverData[0].data.map((d) => {
      const { Speed: speed, Distance: distance } = d;
      const row: any = {
        X: d.X,
        Y: d.Y,
        Distance: d.Y,
      };
      const speedOtherDriver = getSpeedAtDistance(distance, driverData[1].data);
      if (speed > speedOtherDriver) {
        row[driverData[0].driverCode] = d.Y;
      } else if (speedOtherDriver > speed) {
        row[driverData[1].driverCode] = d.Y;
      }
      return row;
    });
    return fastest;
  };

  const fastest = pickFastest(driverData);

  return (
    <ResponsiveContainer>
      <LineChart data={fastest}>
        <Tooltip />
        <Legend verticalAlign="bottom" align="left" />
        <XAxis
          type="number"
          dataKey="X"
          scale="linear"
          tick={false}
          axisLine={false}
          domain={[-6794, 5259]}
        />
        <YAxis
          type="number"
          dataKey="Y"
          scale="linear"
          tick={false}
          axisLine={false}
          domain={[-1493, 10560]}
        />
        <Line
          strokeWidth={12}
          dataKey="Distance"
          dot={false}
          stroke={trackColor}
          legendType="none"
        />
        {driverData.map((d) => {
          return (
            <Line
              key={d.driverCode}
              strokeWidth={8}
              dataKey={d.driverCode}
              dot={false}
              stroke={d.driverColor}
              legendType="square"
              name={`${d.driverCode} is faster`}
            />
          );
        })}
      </LineChart>
    </ResponsiveContainer>
  );
};
