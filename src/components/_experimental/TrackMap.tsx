import * as d3 from "d3";
import React, { useRef, useEffect, useState, useMemo } from "react";
import { Dimensions, useRefDimensions } from "libs/react/dimensions";
import { svg } from "d3";

interface DriverData {
  driverCode: string;
  driverColor: string;
  data: Telemetry[];
}

type DriverTelemetry = Partial<Telemetry> &
  TrackMap & {
    Code?: string;
  };

type Telemetry = TrackMap & {
  Speed: number;
  Distance: number;
};

type TrackMap = {
  X: number;
  Y: number;
};

interface TrackMapProps {
  color: string;
  driverData: DriverData[];
  telemetryOverlay?: "none" | "fastest";
}

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

// TODO: maybe use groups?
export const TrackMap = (props: TrackMapProps) => {
  const ref = useRef(null);
  const dimensions = useRefDimensions(ref);
  const svgRef = useRef(null);
  const map = props.driverData[0].data;

  // x scale bounds
  const xScale = useMemo(() => {
    const [xMin, xMax] = d3.extent(map, (m) => {
      return m.X;
    });
    return d3
      .scaleLinear()
      .domain([xMin ?? 0, xMax ?? 0])
      .range([10, dimensions.width - 10]);
  }, [map, dimensions.width]);

  // y scale bounds
  const yScale = useMemo(() => {
    const [yMin, yMax] = d3.extent(map, (m) => m.Y);
    return d3
      .scaleLinear()
      .domain([yMin ?? 0, yMax ?? 0])
      .range([dimensions.height - 10, 10]);
  }, [map, dimensions.height]);

  // draw when scales have changed
  useEffect(() => {
    if (!xScale || !yScale) {
      return;
    }
    console.log("draw!");

    d3.select(svgRef.current).selectAll("*").remove();
    drawMap(map);

    if (props.telemetryOverlay === "fastest") {
      drawFastestOverlay(props.driverData);
    }
  }, [props, xScale, yScale]);

  // draw track map
  const drawMap = (map: TrackMap[]) => {
    const g = d3
      .select(svgRef.current)
      .selectAll(".track-map")
      .data<TrackMap[]>([map])
      .enter()
      .append("g")
      .attr("class", "track-map");

    g.append("path")
      .attr(
        "d",
        d3
          .line<TrackMap>()
          .x((d) => xScale(d.X))
          .y((d) => yScale(d.Y))
      )
      .attr("fill", "none")
      .attr("stroke", props.color)
      .attr("shape-rendering", "gerometricPrecision")
      .attr("stroke-width", 12)
      .exit()
      .remove();
  };

  const drawFastestOverlay = (drivers: DriverData[]) => {
    const fastest = pickFastest(drivers);

    drivers.forEach((driver) => {
      const data = fastest.map((d) =>
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

      const g = d3
        .select(svgRef.current)
        .selectAll(`.fastest-overlay-${driver.driverCode}`)
        .data<DriverTelemetry[]>(terminated)
        .enter()
        .append("g")
        .attr("class", `fastest-overlay-${driver.driverCode}`);

      g.append("path")
        .attr(
          "d",
          d3
            .line<DriverTelemetry>()
            .x((d) => xScale(d.X))
            .y((d) => yScale(d.Y))
        )
        .attr("fill", "none")
        .attr("stroke", driver.driverColor)
        .attr("stroke-width", 8)
        .attr("shape-rendering", "geometricPrecision")
        .exit()
        .remove();
    });
  };

  return (
    <div ref={ref} className="h-full w-full">
      <svg width="100%" height="100%" ref={svgRef}></svg>
    </div>
  );
};

TrackMap.defaultProps = {
  telemetryOverlay: "none",
};
