import * as d3 from "d3";
import React, { useRef, useEffect, useMemo } from "react";
import { useRefDimensions } from "libs/react/dimensions";
import type { DriverData, Telemetry } from "libs/types";

interface CornerAnalysisProps {
  turnNumber: number;
  driverData: DriverData[];
  distanceFrom: number;
  distanceTo: number;
}

export const CornerAnalysis = (props: CornerAnalysisProps) => {
  const ref = useRef(null);
  const dimensions = useRefDimensions(ref);
  const svgRef = useRef(null);
  const allDriverData: DriverTelemetry[] = props.driverData
    .map((d) => {
      return d.data.map((tel) => {
        return {
          ...tel,
          Code: d.driverCode,
          Color: d.driverColor,
        };
      });
    })
    .flat();

  const [mx, my] = [14, 14];

  // x scale bounds
  const distanceScale = useMemo(() => {
    const [xMin, xMax] = [props.distanceFrom, props.distanceTo];
    return d3
      .scaleLinear()
      .domain([xMin ?? 0, xMax ?? 0])
      .range([mx, dimensions.width - mx]);
  }, [allDriverData, dimensions.width, mx]);

  // y scale bounds
  const speedScale = useMemo(() => {
    const [yMin, yMax] = d3.extent(allDriverData, (d) => d.Speed);
    return d3
      .scaleLinear()
      .domain([yMin ?? 0, yMax ?? 0])
      .range([dimensions.height - my, my]);
  }, [allDriverData, dimensions.height, my]);

  // draw
  useEffect(() => {
    if (!distanceScale || !speedScale) {
      return;
    }

    d3.select(svgRef.current).selectAll("*").remove();
    drawSpeedGraph(allDriverData);
  }, [props, distanceScale, speedScale]);

  const drawSpeedGraph = () => {
    const color = d3
      .scaleOrdinal()
      .domain(props.driverData.map((d) => d.driverCode))
      .range(props.driverData.map((d) => d.driverColor));

    const g = d3
      .select(svgRef.current)
      .selectAll(`.speed-graph`)
      .data<DriverData>(props.driverData)
      .enter()
      .append("g")
      .attr("class", "speed-graph");

    g.append("path")
      .attr("d", (d) => {
        return d3
          .line<Telemetry>()
          .x((d) => {
            return distanceScale(d.Distance);
          })
          .y((d) => speedScale(d.Speed))(d.data);
      })
      .attr("fill", "none")
      .attr("stroke-width", 2)
      .attr("stroke", (d) => color(d.driverCode));
  };

  return (
    <div className="w-full h-full">
      <div className="bg-oldLavender">
        <p className="text-3xl px-5 py-2 mb-5 tracking-wider">
          Corner Analysis - Turn {props.turnNumber} 🏎️ 🏎️ 🏎️
        </p>
      </div>
      <div ref={ref} className="h-full w-full">
        <svg width="100%" height="100%" ref={svgRef}></svg>
      </div>
    </div>
  );
};
