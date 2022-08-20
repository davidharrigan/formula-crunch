import React, { useRef, useEffect, useState, useMemo } from "react";
import { extent, max } from "d3-array";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { Group } from "@visx/group";

import { useRefDimensions } from "libs/react/dimensions";
import type { TrackData, DriverData, Telemetry } from "libs/types";

type DriverTelemetry = Partial<Telemetry> & {
  Code?: string;
  X: number;
  Y: number;
};

const pickTelemetryAtDistance = (
  distance: number,
  data: Telemetry[]
): Telemetry | undefined => {
  for (let i = 1; i < data.length; i++) {
    if (data[i].Distance >= distance) {
      // TODO: need to interpolate distance...?
      return data[i];
    }
  }
};

const pickFastest = (drivers: DriverData[]): DriverTelemetry[] => {
  const tel: DriverTelemetry[] = [];
  const fastest = drivers[0].data.forEach((d) => {
    const { Speed: speed, Distance: distance } = d;
    // TODO: support more than 2 drivers?
    const telOtherDriver = pickTelemetryAtDistance(distance, drivers[1].data);
    const row: DriverTelemetry = {
      X: d.X,
      Y: d.Y,
    };

    if (telOtherDriver === undefined) {
      tel.push(row);
      return;
    }

    if (speed > telOtherDriver.Speed) {
      tel.push({
        Code: drivers[0].driverCode,
        ...d,
      });
    } else if (telOtherDriver.Speed > speed) {
      tel.push({
        Code: drivers[1].driverCode,
        ...telOtherDriver,
        ...row,
      });
    } else {
      tel.push(row);
    }
  });
  return tel;
};

interface TrackMapProps {
  color: string;
  driverData: DriverData[];
  telemetryOverlay?: "none" | "fastest";
}

export const TrackMap = (props: TrackMapProps) => {
  const ref = useRef(null);
  const dimensions = useRefDimensions(ref);
  const map = props.driverData[0].data;
  const [xMargin, yMargin] = [14, 14];

  // x scale bounds
  const xScale = scaleLinear<number>({
    domain: extent(map, (m: Telemetry) => m.X) as [number, number],
  }).range([xMargin, dimensions.width - xMargin]);

  // y scale bounds
  const yScale = scaleLinear<number>({
    domain: extent(map, (m: Telemetry) => m.Y) as [number, number],
  }).range([dimensions.height - yMargin, yMargin]);

  const overlay = pickFastest(props.driverData);

  return (
    <div ref={ref} className="h-full w-full">
      <svg width="100%" height="100%">
        <Group>
          <LinePath<Telemetry>
            data={map}
            x={(d) => xScale(d.X) ?? 0}
            y={(d) => yScale(d.Y) ?? 0}
            stroke={props.color}
            strokeWidth={12}
            shapeRendering="geometricPrecision"
          />
          {overlay &&
            props.driverData.map((driver) => {
              const data = overlay.map((d) =>
                d.Code === driver.driverCode ? d : null
              );

              const terminated: DriverTelemetry[][] = [[]];
              let idx = 0;
              let prevNull = true;
              data.forEach((d) => {
                if (d === null) {
                  if (!prevNull) {
                    idx++;
                  }
                  prevNull = true;
                  return;
                }
                if (terminated.length === idx) {
                  terminated.push([]);
                }
                prevNull = false;
                terminated[idx].push(d);
              });
              return terminated.map((t) => {
                return (
                  <LinePath<DriverTelemetry>
                    data={t}
                    x={(d) => xScale(d.X)}
                    y={(d) => yScale(d.Y)}
                    stroke={driver.driverColor}
                    strokeWidth={6}
                    shapeRendering="geometricPrecision"
                  />
                );
              });
            })}
        </Group>
      </svg>
    </div>
  );
};

TrackMap.defaultProps = {
  telemetryOverlay: "none",
};
